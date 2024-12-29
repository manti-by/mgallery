import logging
import os

import gi
from gi.repository.GLib import GError
from humanize import naturalsize

from mgallery.database import Database
from mgallery.settings import GALLERY_PATH, THUMBNAILS_PATH


gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, GdkPixbuf  # noqa

logger = logging.getLogger(__name__)
files_to_delete = set()


class DuplicatesBox(Gtk.Box):
    def __init__(self, images: list):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.set_homogeneous(True)

        grid = Gtk.Grid()
        grid.set_column_spacing(5)
        grid.set_row_spacing(0)
        for index, image in enumerate(images):
            if ".gif" in image["name"]:
                continue

            try:
                pix_buf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    f"{THUMBNAILS_PATH}/{image['path']}/{image['name']}.jpg",
                    width=128,
                    height=128,
                    preserve_aspect_ratio=True,
                )
            except GError:
                logger.warning(f"Can't open an image {image['path']}/{image['name']}")
                continue
            except Exception as e:
                logger.error(e)
                continue

            image_box_height = 7

            image_box = Gtk.Image.new_from_pixbuf(pix_buf)
            image_box.set_alignment(0, 0.95)  # noqa
            grid.attach(image_box, index, 0, 1, image_box_height)

            label = Gtk.Label()
            image_size = naturalsize(image["size"], gnu=True)
            label_text = f"<b>{image_size}</b> {image['width']}x{image['height']} "
            label.set_markup(f"<span size='medium'>{label_text}</span>")
            label.set_alignment(0, 0.05)  # noqa
            grid.attach(label, index, image_box_height + 1, 1, 1)

            label = Gtk.Label()
            label_text = image["path"][-30:] or "root"
            label.set_markup(f"<span size='medium'><b>{label_text}</b></span>")
            label.set_alignment(0, 0.05)  # noqa
            grid.attach(label, index, image_box_height + 2, 1, 1)

            label = Gtk.Label()
            label_text = image["name"][-30:]
            label.set_markup(f"<span size='small'>{label_text}</span>")
            label.set_alignment(0, 0.05)  # noqa
            grid.attach(label, index, image_box_height + 3, 1, 1)

            check_box = Gtk.CheckButton(label="delete")
            check_box.connect("toggled", self.on_check_toggled, image["path"], image["name"])
            grid.attach(check_box, index, image_box_height + 4, 1, 1)

        self.add(grid)  # noqa

    def on_check_toggled(self, check_box, path, name):  # noqa
        if check_box.get_active():
            files_to_delete.add((path, name))
        else:
            files_to_delete.remove((path, name))


class DuplicatesGrid(Gtk.Grid):
    def __init__(self, duplicates: dict):
        super().__init__()

        self.set_column_spacing(20)
        self.set_row_spacing(50)

        left = top = 0
        for _, images in duplicates.items():
            duplicates_box = DuplicatesBox(images)
            self.attach(duplicates_box, left, top, 1, 1)
            left += 1
            if (left + 1) % 4 == 0:
                left = 0
                top += 1


class DuplicatesApp(Gtk.VBox):  # noqa
    def __init__(self, database: Database, duplicates: dict):
        super().__init__()

        self.database = database
        self.duplicates = dict(sorted(duplicates.items(), key=lambda item: len(item[1]), reverse=True))

        self.page_size = 9
        self.current_page = 1
        self.total_pages = len(duplicates) // self.page_size + 1

        scrolled_window = Gtk.ScrolledWindow()
        self.add(scrolled_window)

        self.stack = Gtk.Stack()
        self.stack.set_border_width(10)  # noqa
        for page in range(1, self.total_pages + 1):
            start = (page - 1) * self.page_size
            end = start + self.page_size
            duplicates_slice = dict(list(self.duplicates.items())[start:end])
            duplicates_grid = DuplicatesGrid(duplicates_slice)
            self.stack.add_titled(duplicates_grid, f"page-{page}", f"{page}")

        scrolled_window.add(self.stack)  # noqa

        buttons_grid = Gtk.Grid(column_spacing=10, row_spacing=10)

        delete_button = Gtk.Button(label="Delete")
        delete_button.connect("clicked", self.delete_images)
        buttons_grid.attach(delete_button, 0, 0, 10, 1)

        spacer_label = Gtk.Label()
        spacer_label.set_hexpand(True)
        buttons_grid.attach(spacer_label, 20, 0, 20, 1)

        prev_page_button = Gtk.Button(label="<< Prev")
        prev_page_button.connect("clicked", self.prev_page)
        buttons_grid.attach(prev_page_button, 50, 0, 10, 1)

        self.pagination_label = Gtk.Label()
        self.pagination_label.set_text(f"{self.current_page} / {self.total_pages}")
        self.pagination_label.set_justify(Gtk.Justification.CENTER)
        buttons_grid.attach(self.pagination_label, 60, 0, 5, 1)

        next_page_button = Gtk.Button(label="Next >>")
        next_page_button.connect("clicked", self.next_page)
        buttons_grid.attach(next_page_button, 75, 0, 10, 1)

        self.pack_start(buttons_grid, False, False, 0)

    def delete_images(self, *args, **kwargs):
        for path, name in files_to_delete:
            self.database.delete(path, name)

            thumbnail_name = f"{THUMBNAILS_PATH}/{path}/{name}.jpg"
            if os.path.exists(thumbnail_name):
                os.remove(thumbnail_name)

            file_name = f"{GALLERY_PATH}/{path}/{name}"
            if os.path.exists(file_name):
                os.remove(file_name)
                logger.info(f"{file_name} is deleted")
                continue

            logger.error(f"Can't find a file {file_name}")

    def next_page(self, *args, **kwargs):
        self.current_page = self.total_pages if self.current_page == self.total_pages else self.current_page + 1
        self.pagination_label.set_text(f"{self.current_page} / {self.total_pages}")
        self.stack.set_visible_child_name(f"page-{self.current_page}")

    def prev_page(self, *args, **kwargs):
        self.current_page = 1 if self.current_page == 1 else self.current_page - 1
        self.pagination_label.set_text(f"{self.current_page} / {self.total_pages}")
        self.stack.set_visible_child_name(f"page-{self.current_page}")


def run_compare(width: int = 1200, height: int = 800):
    database = Database()
    duplicates = database.duplicates()
    logger.info(f"Compare {len(duplicates)} images")

    window = Gtk.Window(title="Duplicated Images", default_width=width, default_height=height)
    window.set_border_width(20)  # noqa

    app = DuplicatesApp(database, duplicates)
    window.add(app)  # noqa

    window.connect("destroy", Gtk.main_quit)  # noqa
    window.show_all()  # noqa
    Gtk.main()  # noqa
