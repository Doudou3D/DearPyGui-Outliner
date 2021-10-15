import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

import pathlib as pth
from PIL import Image
import numpy as np

FONT_PATH = pth.Path("Datas/Fonts")
ICONS_PATH = pth.Path("Datas/Icons/18px")

font_list = FONT_PATH.glob("*.ttf")
icons_list = ICONS_PATH.glob("*.png")

dpg.create_context()

dpg.create_viewport(title='Matador', width=1024, height=1024)
dpg.configure_app(docking=True, docking_space=True, init_file="settings.ini")
dpg.setup_dearpygui()
dpg.show_viewport()

# add a font registry
with dpg.font_registry():

    for font in font_list:

        # add font (set as default for entire app)
        dpg.add_font( str(font), 16, tag=font.stem )

dpg.bind_font("Cousine-Regular")

with dpg.value_registry():
    dpg.add_color_value(default_value=[163,146,61,255], label="Color Icons1", tag="Color_Icons1")
    dpg.add_color_value(default_value=[109,109,109,0], label="Color Icons2", tag="Color_Icons2")

dpg.add_texture_registry(label="Texture Container", tag="Texture_Container")

class Gen_Icon():

    def __init__(self, icon) -> None:

        self.name = icon.stem
        self.image = Image.open(str(icon))
        self.alpha = self.image.split()[-1]

        self.width = self.image.width
        self.height = self.image.height

        self.array = np.asarray(self.image, dtype=np.float32)/255
        self.array_alpha = np.asarray(self.alpha.convert(mode="RGBA"))/255

        self.tag = icon.stem

        color1 = np.asarray(dpg.get_value("Color_Icons1"), dtype=np.float32)
        color1 = color1/255

        color2 = np.asarray(dpg.get_value("Color_Icons2"), dtype=np.float32)
        color2 = color2/255

        self.array = color1 * self.array + color2 * (1 - self.array)

        self.dynamic_Tex = dpg.add_raw_texture(self.image.width, self.image.height, self.array, format=dpg.mvFormat_Float_rgba, parent="Texture_Container", tag=self.tag, label=f"Lbl_Icon_{icon.stem}")

class Mtd_Outliner_View():

    def __init__(self):

        self.window_id = dpg.add_window(label="Outliner View",
                                        pos=(200, 200),
                                        width=500,
                                        height=1000)

        self.count = 0

        self._filter_table_id = dpg.generate_uuid()

        with dpg.menu_bar(parent=self.window_id):
            with dpg.menu(label="Select"):
                dpg.add_menu_item(label="Select All", callback=lambda: dpg.show_tool(dpg.mvTool_Metrics))
            with dpg.menu(label="Display"):
                dpg.add_checkbox(label="Auto-scroll", default_value=True,
                                    callback=lambda sender: self.auto_scroll(dpg.get_value(sender)))

        self.table_id = dpg.add_table(header_row=True,
                                        row_background=True,
                                        borders_innerH=True,
                                        borders_outerH=True,
                                        borders_innerV=True,
                                        borders_outerV=True,
                                        resizable=False,
                                        delay_search=True,
                                        hideable=True,
                                        reorderable=True,
                                        freeze_columns=1,
                                        height=-26,
                                        scrollY=True,
                                        parent=self.window_id,
                                        tag=self._filter_table_id)

        dpg.add_table_column(label="Name", parent=self.table_id)
        dpg.add_table_column(label="Sub Elem", width=16, width_fixed=True, parent=self.table_id)
        dpg.add_table_column(label="", use_internal_label=False, width=16, width_fixed=True, parent=self.table_id)
        dpg.add_table_column(label="", use_internal_label=False, width=16, width_fixed=True, parent=self.table_id)
        dpg.add_table_column(label="", use_internal_label=False, width=16, width_fixed=True, parent=self.table_id)

        dpg.add_input_text(label="Filter (Inc,Exc)",
                            width=-135,
                            user_data=self._filter_table_id,
                            callback=lambda s, a, u: dpg.set_value(u, dpg.get_value(s)),
                            parent=self.window_id)

outliner = Mtd_Outliner_View()

list_gen_icon = []

for icon in icons_list:

    list_gen_icon.append(Gen_Icon(icon))

for i in range(0,120):
    with dpg.table_row(label=f"Entry {i}", filter_key=f"Selectable {i}", parent=outliner.table_id):
        dpg.add_text(label=f"Selectable {i}", default_value=f"Selectable {i}")
        dpg.add_text(label="InputText", default_value="1250220202063")
        dpg.add_image_button("restrict_view_on", width=18, height=18)
        dpg.add_image_button("ghost-outline", width=18, height=18)
        dpg.add_image_button("eye-outline", width=18, height=18)
                
dpg.start_dearpygui()
dpg.destroy_context()
