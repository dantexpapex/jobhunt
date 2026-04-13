from playwright.sync_api import sync_playwright
from config import Config
import time
import logging

logger = logging.getLogger(__name__)


class AutoApplier:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)
            self.context = self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self.page = self.context.new_page()
            logger.info("AutoApplier started")
        except Exception as e:
            logger.error(f"Error starting AutoApplier: {e}")

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("AutoApplier stopped")

    def apply_to_job(self, job_url, cv_path=None):
        if not self.page:
            self.start()

        try:
            self.page.goto(job_url)
            time.sleep(2)

            easy_apply_btn = self.page.locator('button:has-text("Easy Apply")')
            if easy_apply_btn.count() > 0:
                easy_apply_btn.click()
                time.sleep(1)
                return self._fill_application_form(cv_path)

            apply_btn = self.page.locator(
                'button:has-text("Apply"), a:has-text("Apply")'
            )
            if apply_btn.count() > 0:
                apply_btn.click()
                time.sleep(1)
                return self._fill_application_form(cv_path)

            logger.warning(f"No apply button found for {job_url}")
            return False

        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return False

    def _fill_application_form(self, cv_path=None):
        try:
            self.page.wait_for_load_state("networkidle")

            file_inputs = self.page.locator('input[type="file"]')
            if cv_path and file_inputs.count() > 0:
                file_inputs[0].set_input_files(cv_path)
                time.sleep(1)

            submit_btns = self.page.locator(
                'button:has-text("Submit"), button:has-text("Send")'
            )
            if submit_btns.count() > 0:
                submit_btns[0].click()
                time.sleep(2)
                logger.info("Application submitted successfully")
                return True

            logger.warning("Submit button not found")
            return False

        except Exception as e:
            logger.error(f"Error filling form: {e}")
            return False

    def login_linkedin(self, email, password):
        if not self.page:
            self.start()

        try:
            self.page.goto("https://www.linkedin.com/login")
            self.page.fill("#username", email)
            self.page.fill("#password", password)
            self.page.click('button[type="submit"]')
            self.page.wait_for_load_state("networkidle")
            logger.info("Logged into LinkedIn")
            return True
        except Exception as e:
            logger.error(f"Error logging into LinkedIn: {e}")
            return False

    def is_logged_in(self):
        try:
            self.page.goto("https://www.linkedin.com/feed")
            self.page.wait_for_load_state("networkidle")
            return "sign in" not in self.page.url.lower()
        except:
            return False


def apply_with_delay(job_url, cv_path=None, delay_seconds=300):
    time.sleep(delay_seconds)
    applier = AutoApplier()
    try:
        result = applier.apply_to_job(job_url, cv_path)
        return result
    finally:
        applier.stop()


def apply_to_multiple_jobs(job_urls, cv_path=None, delay_between=300):
    results = []
    applier = AutoApplier()
    applier.start()

    try:
        for url in job_urls:
            result = applier.apply_to_job(url, cv_path)
            results.append({"url": url, "success": result})
            if delay_between > 0:
                time.sleep(delay_between)
    finally:
        applier.stop()

    return results
