import customtkinter
import os
from PIL import Image


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("A9 AUTO")
        self.geometry("700x450")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
        self.logo_image = customtkinter.CTkImage(
            Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")),
            size=(26, 26),
        )
        self.image_icon_image = customtkinter.CTkImage(
            Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20)
        )
        self.home_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "home.png")),
            size=(20, 20),
        )
        self.chat_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "settings.png")),
            size=(20, 20),
        )
        self.add_user_image = customtkinter.CTkImage(
            light_image=Image.open(os.path.join(image_path, "help.png")),
            size=(20, 20),
        )

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(
            self.navigation_frame,
            text="  A9 Auto",
            image=self.logo_image,
            compound="left",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="开始",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            image=self.home_image,
            anchor="w",
            command=self.home_button_event,
        )
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="配置",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            image=self.chat_image,
            anchor="w",
            command=self.frame_2_button_event,
        )
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(
            self.navigation_frame,
            corner_radius=0,
            height=40,
            border_spacing=10,
            text="帮助",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            image=self.add_user_image,
            anchor="w",
            command=self.frame_3_button_event,
        )
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        # create home frame
        self.home_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.textbox = customtkinter.CTkTextbox(self.home_frame, width=250, height=360)
        self.textbox.grid(row=0, column=0, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.entry = customtkinter.CTkEntry(
            self.home_frame, placeholder_text="Please input command."
        )
        self.entry.grid(
            row=1, column=0, columnspan=2, padx=(20, 20), pady=(0, 20), sticky="nsew"
        )

        # create second frame
        self.second_frame = customtkinter.CTkScrollableFrame(
            self, corner_radius=0, fg_color="transparent"
        )

        # # create scrollable frame
        # self.scrollable_frame = customtkinter.CTkScrollableFrame(
        #     self, label_text="CTkScrollableFrame"
        # )
        # self.scrollable_frame.grid(
        #     row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew"
        # )
        # self.scrollable_frame.grid_columnconfigure(0, weight=1)
        # self.scrollable_frame_switches = []

        self.label_mode = customtkinter.CTkLabel(master=self.second_frame, text="模式:")
        self.label_mode.grid(row=0, column=0, columnspan=1, padx=10, pady=10, sticky="")

        self.label_mode = customtkinter.CTkLabel(master=self.second_frame, text="任务:")
        self.label_mode.grid(row=1, column=0, columnspan=1, padx=10, pady=10, sticky="")

        self.label_mode = customtkinter.CTkLabel(master=self.second_frame, text="多一:")
        self.label_mode.grid(row=4, column=0, columnspan=1, padx=10, pady=10, sticky="")

        # self.label_mode = customtkinter.CTkLabel(master=self.second_frame, text="多二:")
        # self.label_mode.grid(row=3, column=0, columnspan=1, padx=10, pady=10, sticky="")

        # self.label_mode = customtkinter.CTkLabel(master=self.second_frame, text="寻车:")
        # self.label_mode.grid(row=4, column=0, columnspan=1, padx=10, pady=10, sticky="")

        self.mode_buttons = customtkinter.CTkSegmentedButton(self.second_frame)
        self.mode_buttons.grid(
            row=0, column=1, padx=(20, 10), pady=(10, 10), sticky="ew"
        )

        self.task_1 = customtkinter.CTkCheckBox(master=self.second_frame, text="免费抽卡")
        self.task_1.grid(row=1, column=1, pady=(10, 10), padx=(20, 0), sticky="ew")

        self.task_combobox_1 = customtkinter.CTkComboBox(
            self.second_frame, values=["180", "240"]
        )
        self.task_combobox_1.grid(row=1, column=2, padx=0, pady=(10, 10))

        self.task_2 = customtkinter.CTkCheckBox(master=self.second_frame, text="大奖赛抽卡")
        self.task_2.grid(row=2, column=1, pady=(10, 10), padx=(20, 0), sticky="ew")

        self.task_combobox_2 = customtkinter.CTkComboBox(
            self.second_frame, values=["240"]
        )
        self.task_combobox_2.grid(row=2, column=2, padx=0, pady=(10, 10))

        self.task_3 = customtkinter.CTkCheckBox(master=self.second_frame, text="寻车")
        self.task_3.grid(row=3, column=1, pady=(10, 10), padx=(20, 0), sticky="ew")

        self.task_combobox_2 = customtkinter.CTkComboBox(
            self.second_frame, values=["10"]
        )
        self.task_combobox_2.grid(row=3, column=2, padx=0, pady=(10, 10))

        # create tabview
        self.tabview = customtkinter.CTkTabview(self.second_frame, width=340)
        self.tabview.grid(
            row=4, column=1, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew"
        )

        tabs = ["青铜", "白银", "黄金", "铂金"]
        for tab_index, tab_name in enumerate(tabs):
            self.tabview.add(tab_name)

            self.tabview.tab(tab_name).grid_columnconfigure(1, weight=1)

            car_level = customtkinter.CTkLabel(
                master=self.tabview.tab(tab_name), text="车库等级:"
            )
            car_level.grid(row=0, column=0, padx=10, pady=(10, 10))

            option_level = customtkinter.CTkOptionMenu(
                self.tabview.tab(tab_name),
                dynamic_resizing=False,
                values=tabs[: tab_index + 1],
            )
            option_level.grid(row=0, column=1, padx=10, pady=(10, 10))

            car_position = customtkinter.CTkLabel(
                master=self.tabview.tab(tab_name), text="车库位置:"
            )

            car_position.grid(row=1, column=0, padx=10, pady=(10, 10))

            row = customtkinter.CTkLabel(master=self.tabview.tab(tab_name), text="row")

            row.grid(row=1, column=1, padx=(0, 0), pady=(10, 10), sticky="nsew")

            col = customtkinter.CTkLabel(master=self.tabview.tab(tab_name), text="col")

            col.grid(row=1, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")

            for r in range(6):
                option1 = customtkinter.CTkOptionMenu(
                    self.tabview.tab(tab_name),
                    dynamic_resizing=False,
                    values=[str(i) for i in range(0, 3)],
                    width=100,
                    height=28,
                )

                option2 = customtkinter.CTkOptionMenu(
                    self.tabview.tab(tab_name),
                    dynamic_resizing=False,
                    values=[str(i) for i in range(0, 20)],
                    width=100,
                    height=28,
                )

                option1.grid(row=r + 2, column=1, padx=(0, 0), pady=(10, 10))
                option2.grid(row=r + 2, column=2, padx=(0, 0), pady=(10, 10))

        self.label_mode = customtkinter.CTkLabel(master=self.second_frame, text="多二:")
        self.label_mode.grid(row=5, column=0, columnspan=1, padx=10, pady=10, sticky="")

        tabview = customtkinter.CTkTabview(self.second_frame, width=340)
        tabview.grid(
            row=5, column=1, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew"
        )

        tabview.add("多二配置")

        tabview.tab("多二配置").grid_columnconfigure(1, weight=1)

        car_position = customtkinter.CTkLabel(master=tabview.tab("多二配置"), text="车库位置:")

        car_position.grid(row=1, column=0, padx=10, pady=(10, 10))

        row = customtkinter.CTkLabel(master=tabview.tab("多二配置"), text="row")

        row.grid(row=1, column=1, padx=(0, 0), pady=(10, 10), sticky="nsew")

        col = customtkinter.CTkLabel(master=tabview.tab("多二配置"), text="col")

        col.grid(row=1, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")

        for r in range(6):
            option1 = customtkinter.CTkOptionMenu(
                tabview.tab("多二配置"),
                dynamic_resizing=False,
                values=[str(i) for i in range(0, 3)],
                width=100,
                height=28,
            )

            option2 = customtkinter.CTkOptionMenu(
                tabview.tab("多二配置"),
                dynamic_resizing=False,
                values=[str(i) for i in range(0, 20)],
                width=100,
                height=28,
            )

            option1.grid(row=r + 2, column=1, padx=(0, 0), pady=(10, 10))
            option2.grid(row=r + 2, column=2, padx=(0, 0), pady=(10, 10))

        self.label_mode = customtkinter.CTkLabel(master=self.second_frame, text="寻车:")
        self.label_mode.grid(row=6, column=0, columnspan=1, padx=10, pady=10, sticky="")

        tabview = customtkinter.CTkTabview(self.second_frame, width=340)
        tabview.grid(
            row=6, column=1, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew"
        )

        tabview.add("寻车配置")

        tabview.tab("寻车配置").grid_columnconfigure(1, weight=1)

        car_position = customtkinter.CTkLabel(master=tabview.tab("寻车配置"), text="车库位置:")

        car_position.grid(row=1, column=0, padx=10, pady=(10, 10))

        row = customtkinter.CTkLabel(master=tabview.tab("寻车配置"), text="row")

        row.grid(row=1, column=1, padx=(0, 0), pady=(10, 10), sticky="nsew")

        col = customtkinter.CTkLabel(master=tabview.tab("寻车配置"), text="col")

        col.grid(row=1, column=2, padx=(0, 10), pady=(10, 10), sticky="nsew")

        for r in range(6):
            option1 = customtkinter.CTkOptionMenu(
                tabview.tab("寻车配置"),
                dynamic_resizing=False,
                values=[str(i) for i in range(0, 3)],
                width=100,
                height=28,
            )

            option2 = customtkinter.CTkOptionMenu(
                tabview.tab("寻车配置"),
                dynamic_resizing=False,
                values=[str(i) for i in range(0, 20)],
                width=100,
                height=28,
            )

            option1.grid(row=r + 2, column=1, padx=(0, 0), pady=(10, 10))
            option2.grid(row=r + 2, column=2, padx=(0, 0), pady=(10, 10))

        # create third frame
        self.third_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )

        # select default frame
        self.select_frame_by_name("frame_2")
        self.mode_buttons.configure(values=["多人一", "多人二", "寻车"])
        self.mode_buttons.set("多人一")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(
            fg_color=("gray75", "gray25") if name == "home" else "transparent"
        )
        self.frame_2_button.configure(
            fg_color=("gray75", "gray25") if name == "frame_2" else "transparent"
        )
        self.frame_3_button.configure(
            fg_color=("gray75", "gray25") if name == "frame_3" else "transparent"
        )

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.select_frame_by_name("frame_3")


if __name__ == "__main__":
    app = App()
    app.mainloop()
