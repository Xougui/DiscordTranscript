from playwright.sync_api import sync_playwright
import os

def run():
    # File is in repo root /app/test_render.html
    file_path = os.path.abspath("test_render.html")
    url = f"file://{file_path}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 3000})
        page.goto(url)

        # Test Image Popup and Close Button
        image = page.locator(".chatlog__attachment-thumbnail").first
        if image.count() > 0:
            image.click()
            page.wait_for_selector("#image-modal", state="visible")
            page.screenshot(path="verification/verification_modal_open.png")

            close_btn = page.locator(".modal-close")
            if close_btn.count() > 0:
                close_btn.click()
                page.wait_for_selector("#image-modal", state="hidden")

        # Force full height for chatlog screenshot
        page.evaluate("""() => {
            document.body.style.overflow = 'visible';
            document.body.style.height = 'auto';
            document.querySelector('.main').style.overflow = 'visible';
            document.querySelector('.main').style.height = 'auto';
            document.querySelector('.chatlog').style.overflow = 'visible';
        }""")

        # Wait for potential rendering
        page.wait_for_timeout(1000)

        page.screenshot(path="verification/verification_full_scroll.png", full_page=True)

        browser.close()

if __name__ == "__main__":
    run()
