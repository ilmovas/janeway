import os
import shutil
import sass
from jsmin import jsmin

from django.conf import settings
from django.core.management import call_command

from journal import models as journal_models


def process_scss():
    """Compiles SCSS into CSS in the Static Assets folder"""
    paths = [
        os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/foundation-sites/scss/"),
        os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/motion-ui/src/"),
    ]

    # File dirs
    app_scss_file = os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/scss/app.scss")
    app_css_file = os.path.join(settings.BASE_DIR, "static/ilmovas/css/app.css")

    compiled_css_from_file = sass.compile(filename=app_scss_file, include_paths=paths)

    # Open the CSS file and write into it
    write_file = open(app_css_file, "w", encoding="utf-8")
    write_file.write(compiled_css_from_file)


def minify_js_proc(src_text):
    """
    :param src_text: Source text to be minified
    :return: Minified text
    """
    return jsmin(src_text)


def process_js_files(source_paths, dest_path, min_path):
    f = open(dest_path, "w", encoding="utf-8")
    js_file = None
    try:
        js_file = open(min_path, "w", encoding="utf-8")
        for src_file in source_paths:
            with open(src_file, "r", encoding="utf-8") as inputFile:
                src_text = inputFile.read()
                min_text = src_text  # minify_js_proc(src_text)
            f.write(src_text)
            js_file.write(min_text)
    finally:
        f.close()
        if js_file and not js_file.closed:
            js_file.close()


def process_js():
    """Copies JS from compile into static assets"""
    source_paths = [
        os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/js/admin.js"),
        os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/js/app.js"),
        os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/js/footnotes.js"),
        os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/js/table_of_contents.js"),
        os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/js/toastr.js"),
    ]
    dest_path = os.path.join(settings.BASE_DIR, "static/ilmovas/js/app.js")
    min_path = os.path.join(settings.BASE_DIR, "static/ilmovas/js/app.min.js")

    process_js_files(source_paths, dest_path, min_path)


def copy_files(src_path, dest_path):
    """
    :param src_path: The source folder for copying
    :param dest_path: The destination these files/folders should be copied to
    :return: None
    """
    if not os.path.exists(src_path):
        os.makedirs(src_path)

    files = os.listdir(src_path)

    for file_name in files:
        full_file_name = os.path.join(src_path, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, dest_path)
        else:
            dir_dest = os.path.join(dest_path, file_name)
            if os.path.exists(dir_dest):
                shutil.rmtree(os.path.join(dir_dest))
            shutil.copytree(full_file_name, dir_dest)


def copy_file(source, destination):
    """
    :param source: Absolute path to the source file.
    :param destination: Absolute path to the destination file.
    :return:
    Both paths must be absolute and must resolve within BASE_DIR.
    """
    base = os.path.realpath(settings.BASE_DIR)

    real_source = os.path.realpath(source)
    real_dest = os.path.realpath(destination)

    if not real_source.startswith(base + os.sep):
        raise ValueError(
            "copy_file: source path escapes BASE_DIR: {}".format(source)
        )
    if not real_dest.startswith(base + os.sep):
        raise ValueError(
            "copy_file: destination path escapes BASE_DIR: {}".format(destination)
        )

    destination_folder = os.path.dirname(real_dest)
    os.makedirs(destination_folder, exist_ok=True)

    shutil.copy(real_source, real_dest)


def process_fonts():
    """Processes fonts from the compile folder into Static Assets"""
    fonts_path = os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/fonts/")
    static_fonts = os.path.join(settings.BASE_DIR, "static/ilmovas/fonts/")

    copy_files(fonts_path, static_fonts)


def process_images():
    """Processes images from the compile folder into Static Assets.

    Wave 1 (2026-07-04): demo folders default_carousel/ and sample/ removed
    from assets/img/ — journals upload their own header/cover images.
    """
    image_path = os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/img/")
    static_images = os.path.join(settings.BASE_DIR, "static/ilmovas/img/")

    copy_files(image_path, static_images)


def process_standalone_css():
    """Copies standalone CSS (e.g. local-fonts.css) into Static Assets"""
    css_path = os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/css/")
    static_css = os.path.join(settings.BASE_DIR, "static/ilmovas/css/")

    if os.path.isdir(css_path):
        copy_files(css_path, static_css)


def process_vendor_assets():
    """Copy vendor CSS/JS referenced directly by templates (not bundled into app.js)."""
    theme_assets = os.path.join(settings.BASE_DIR, "themes/ilmovas/assets")
    static_css = os.path.join(settings.BASE_DIR, "static/ilmovas/css")
    static_js = os.path.join(settings.BASE_DIR, "static/ilmovas/js")

    vendor_css = [
        (os.path.join(theme_assets, "toastr.min.css"), "toastr.min.css"),
        (
            os.path.join(theme_assets, "font-awesome/css/font-awesome.min.css"),
            "font-awesome.min.css",
        ),
    ]
    for src, name in vendor_css:
        if os.path.isfile(src):
            copy_file(src, os.path.join(static_css, name))

    for name in ("jquery-3.7.1.min.js", "toastr.min.js", "tailwind-cdn.js"):
        src = os.path.join(theme_assets, "js", name)
        if os.path.isfile(src):
            copy_file(src, os.path.join(static_js, name))


def process_mathjax():
    """Copy self-hosted MathJax 3 CHTML subset into Static Assets.

    Wave 2 (2026-07-04): replaced MathJax 2.7.7 full tree (~178 MB) with a
    pruned MathJax 3.2.2 subset (~1.6 MB in theme assets):
      - es5/tex-mml-chtml.js
      - es5/output/chtml/fonts/tex.js
      - es5/output/chtml/fonts/woff-v2/*.woff
    See ILMOVAS_THEME_NOTES.md for article.html loader config.
    """
    src = os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/js/mathjax")
    dest = os.path.join(settings.BASE_DIR, "static/ilmovas/js/mathjax")

    if os.path.isdir(src):
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest)


def process_journals(override_css_dir, paths):
    journals = journal_models.Journal.objects.all()

    for journal in journals:
        # look for SCSS folder and files
        scss_files = journal.scss_files

        if len(scss_files) == 0:
            print(
                "Journal with ID {0} [{1}] has no SCSS to compile".format(
                    journal.id, journal.name
                )
            )
        else:
            print(
                "Journal with ID {0} [{1}]: processing overrides".format(
                    journal.id, journal.name
                )
            )

            override_css_file = os.path.join(
                override_css_dir, "journal{0}_override.css".format(str(journal.id))
            )

            # we will only process one single SCSS override file for a journal
            scss_path = os.path.realpath(scss_files[0])
            allowed_dir = os.path.realpath(
                os.path.join(settings.BASE_DIR, "files", "styling", "journals", str(journal.id))
            )
            if not scss_path.startswith(allowed_dir + os.sep) and scss_path != allowed_dir:
                print(
                    "Journal {0}: SCSS file outside allowed directory, skipping: {1}".format(
                        journal.id, scss_files[0]
                    )
                )
                continue
            compiled_css_from_file = sass.compile(
                filename=scss_path, include_paths=paths
            )

            # open the journal CSS override file and write into it
            with open(override_css_file, "w", encoding="utf-8") as write_file:
                write_file.write(compiled_css_from_file)

        journal_dir = os.path.join(
            settings.BASE_DIR, "files", "journals", str(journal.id)
        )
        journal_header_image = os.path.join(journal_dir, "header.png")

        if os.path.isfile(journal_header_image):
            print(
                "Journal with ID {0} [{1}]: processing header image".format(
                    journal.id, journal.name
                )
            )
            dest_path = os.path.join(
                settings.BASE_DIR,
                "static",
                "ilmovas",
                "img",
                "journal_header{0}.png".format(journal.id),
            )

            copy_file(journal_header_image, dest_path)


def process_default_override(override_css_dir, include_paths):
    scss_default_override = os.path.join(
        settings.BASE_DIR, "files", "styling", "journals", "default", "override.scss"
    )
    override_css_file = os.path.join(override_css_dir, "default_override.css")

    if os.path.isfile(scss_default_override):
        compiled = sass.compile(
            filename=scss_default_override,
            include_paths=include_paths,
        )
        with open(override_css_file, "w", encoding="utf-8") as f:
            f.write(compiled)


def process_press_override(override_css_dir, include_paths):
    scss_default_override = os.path.join(
        settings.BASE_DIR, "files", "styling", "press", "override.scss"
    )
    override_css_file = os.path.join(override_css_dir, "press_override.css")

    if os.path.isfile(scss_default_override):
        compiled = sass.compile(
            filename=scss_default_override,
            include_paths=include_paths,
        )
        with open(override_css_file, "w", encoding="utf-8") as f:
            f.write(compiled)


def create_paths():
    base_path = os.path.join(settings.BASE_DIR, "static", "ilmovas")
    folders = ["css", "js", "fonts", "img"]

    for folder in folders:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)

    # test if the journal CSS directory exists and create it if not
    override_css_dir = os.path.join(settings.BASE_DIR, "static", "ilmovas", "css")
    os.makedirs(override_css_dir, exist_ok=True)

    return override_css_dir


def build():
    override_css_dir = create_paths()
    print("Processing SCSS")
    process_scss()
    print("Processing JS")
    process_js()
    print("Processing standalone CSS")
    process_standalone_css()
    print("Processing vendor assets")
    process_vendor_assets()
    print("Processing MathJax")
    process_mathjax()
    print("Processing journal overrides")
    include_paths = [
        os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/foundation-sites/scss/"),
        os.path.join(settings.BASE_DIR, "themes/ilmovas/assets/motion-ui/src/"),
    ]
    process_default_override(override_css_dir, include_paths)
    process_journals(override_css_dir, include_paths)
    process_press_override(override_css_dir, include_paths)
    call_command("collectstatic", "--noinput")
