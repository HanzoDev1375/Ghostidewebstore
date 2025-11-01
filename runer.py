import json
import os
import requests

print("Run....")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_OWNER = "HanzoDev1375"
REPO_NAME = "Ghostidewebstore"
API_URL = (
    f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/main?recursive=1"
)
OUTPUT_FILE = "model.json"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github+json",
}


def get_dev_info_from_theme(theme_dir, tree):
    """Find and read dev.json from the theme directory"""
    try:
        # جستجوی فایل dev.json در پوشه تم
        dev_file_path = None
        for item in tree:
            path = item.get("path", "")
            if path == f"{theme_dir}/dev.json" or path.endswith("/dev.json"):
                dev_file_path = path
                break

        if dev_file_path:
            dev_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{dev_file_path}"
            print(f"   ↳ Found dev.json at: {dev_file_path}")

            response = requests.get(dev_url, headers=HEADERS)
            response.raise_for_status()
            dev_data = response.json()
            dev_name = dev_data.get("devname", "https://t.me/zahra_techaii")
            print(f"   ↳ Developer: {dev_name}")
            return dev_name

        print(f"   ↳ No dev.json found in {theme_dir}, using default")
        return "https://t.me/zahra_techaii"

    except Exception as e:
        print(f"   ↳ Error reading dev.json: {e}, using default")
        return "https://t.me/zahra_techaii"


def fetch_ghost_themes():
    try:
        print("Fetching repository tree...")
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()

        tree = response.json().get("tree", [])
        themes = []

        # پیدا کردن فایل‌های زیپ
        zip_files = [item for item in tree if item["path"].endswith(".zip")]

        for zip_file in zip_files:
            theme_dir = os.path.dirname(zip_file["path"])
            theme_name = os.path.basename(theme_dir)

            # خواندن dev.json از پوشه همان تم
            dev_url = get_dev_info_from_theme(theme_dir, tree)

            theme_data = {
                "name": theme_name,
                "url": f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{zip_file['path']}",
                "image": "",
                "orginalfile": dev_url,
            }

            # پیدا کردن عکس‌های مربوط به این تم
            image_files = []
            for item in tree:
                path = item.get("path", "")
                if not path.startswith(f"{theme_dir}/"):
                    continue

                filename = os.path.basename(path).lower()

                if filename.endswith((".webp", ".png", ".jpeg", ".jpg")):
                    image_files.append({"path": path, "filename": filename})

            if image_files:
                preview_candidates = []
                other_images = []

                for img in image_files:
                    if any(
                        keyword in img["filename"]
                        for keyword in ["preview", "cover", "screenshot"]
                    ):
                        preview_candidates.append(img)
                    else:
                        other_images.append(img)

                if preview_candidates:
                    selected_image = preview_candidates[0]
                elif other_images:
                    selected_image = other_images[0]
                else:
                    selected_image = image_files[0]

                theme_data["image"] = (
                    f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/{selected_image['path']}"
                )
                print(f"   ↳ Preview image: {theme_data['image']}")

            print(f"✅ Found theme: {theme_name}")
            print(f"   ↳ ZIP file: {theme_data['url']}")

            themes.append(theme_data)

        return themes

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching repo tree: {e}")
        return []


def save_json(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(data)} themes to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
        return False


if __name__ == "__main__":
    themes = fetch_ghost_themes()
    if themes:
        if save_json(themes, OUTPUT_FILE):
            print("✅ Operation completed successfully!")
        else:
            print("❌ Failed to save JSON file.")
    else:
        print("⚠️ No theme files found or error occurred.")