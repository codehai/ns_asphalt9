import tkinter as tk
from tkinter import filedialog


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GUI Example")
        # 设置窗口大小
        self.root.geometry("500x600")
        self.root.resizable(True, False)  # 允许调整宽度和高度

        # 创建两个页面的容器
        self.page1 = tk.Frame(self.root)
        self.page2 = tk.Frame(self.root)

        # 第一页的组件
        self.label1 = tk.Label(self.page1, text="配置文件:", width=10)
        self.file_button = tk.Button(
            self.page1, text="选择文件", command=self.select_file, width=10
        )
        self.selected_file_label = tk.Label(self.page1, text="", width=30)

        self.var_radio = tk.IntVar()
        self.label_radio = tk.Label(self.page1, text="选择模式:", width=10)
        self.radio_button1 = tk.Radiobutton(
            self.page1, text="多人1", variable=self.var_radio, value=1
        )
        self.radio_button2 = tk.Radiobutton(
            self.page1, text="多人2", variable=self.var_radio, value=2
        )
        self.radio_button3 = tk.Radiobutton(
            self.page1, text="寻车", variable=self.var_radio, value=3
        )

        self.next_button = tk.Button(
            self.page1, text="下一步", command=self.show_page2, width=10
        )

        # 第二页的组件
        self.log_text = tk.Text(
            self.page2, state="disabled", highlightthickness=0, height=41, width=68
        )
        self.command_entry = tk.Entry(self.page2)

        self.last_button = tk.Button(
            self.page2, text="上一步", width=5, command=self.show_page1, height=1
        )

        self.run_button = tk.Button(
            self.page2, text="Run", width=5, command=self.enter, height=1
        )

        self.stop_button = tk.Button(
            self.page2, text="Stop", width=5, command=self.enter, height=1
        )

        self.quit_button = tk.Button(
            self.page2, text="Quit", width=5, command=self.enter, height=1
        )

        # 将组件布局到第一页
        self.label1.grid(row=1, column=0, columnspan=1, sticky="w")
        self.file_button.grid(row=1, column=1, columnspan=2, sticky="w")
        self.selected_file_label.grid(row=1, column=3, columnspan=2, sticky="w")

        self.label_radio.grid(row=2, column=0, columnspan=1, sticky="w")
        self.radio_button1.grid(row=2, column=1, columnspan=1, sticky="w")
        self.radio_button2.grid(row=2, column=2, columnspan=1, sticky="w")
        self.radio_button3.grid(row=2, column=3, columnspan=1, sticky="w")

        self.next_button.grid(row=3, column=0, columnspan=5, sticky="e")

        self.page1.rowconfigure(0, minsize=30)
        self.page1.rowconfigure(1, minsize=30)
        self.page1.rowconfigure(2, minsize=30)
        self.page1.rowconfigure(3, minsize=30)

        # 将组件布局到第二页

        # self.log_text.pack(expand=True)
        self.log_text.grid(row=1, column=0, columnspan=4, sticky="w")
        self.last_button.grid(row=2, column=0, columnspan=1, sticky="nsew")
        self.stop_button.grid(row=2, column=1, columnspan=1, sticky="nsew")
        self.run_button.grid(row=2, column=2, columnspan=1, sticky="nsew")
        self.quit_button.grid(row=2, column=3, columnspan=1, sticky="nsew")

        self.command_entry.grid(row=3, column=0, columnspan=4, sticky="nsew")

        self.page2.rowconfigure(1, minsize=10)
        self.page2.rowconfigure(2, minsize=10)

        # 默认显示第一页
        self.show_page1()

    def enter(self):
        pass

    def select_file(self):
        file_path = filedialog.askopenfilename()  # 弹出文件选择框
        self.selected_file_label.config(text=file_path)
        print("Selected file:", file_path)

    def show_page1(self):
        self.page2.pack_forget()  # 隐藏第二页
        self.page1.pack()  # 显示第一页
        self.root.update()  # 立即刷新界面

    def show_page2(self):
        self.page1.pack_forget()  # 隐藏第一页
        self.page2.pack()  # 显示第二页
        self.log_text.config(state="normal")
        for i in range(50):
            self.log_text.insert("end", str(i) + ":" + "test " * 50 + "\n")
            # break
        self.log_text.see(tk.END)
        self.log_text.config(state="disable")
        self.root.update()  # 立即刷新界面

    def run(self):
        self.root.mainloop()


gui = GUI()
gui.run()
