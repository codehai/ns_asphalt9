import flet
import threading
import time
import flet as ft
from flet import (
    AppBar,
    ElevatedButton,
    Page,
    Text,
    View,
    colors,
    Row,
    VerticalDivider,
    Column,
    GridView,
    IconButton,
)
from flet_core import ScrollMode
from flet_core.border import BorderSide
from flet_core.buttons import RoundedRectangleBorder


def main(page: Page):
    page.title = "Routes Example"
    page.scroll = ScrollMode.AUTO

    print("Initial route:", page.route)

    def toggle_icon_button(e):
        e.control.selected = not e.control.selected
        e.control.update()

    def route_change(e):
        print("Route change:", e.route)
        page.views.clear()
        page.views.append(
            View(
                "/",
                [
                    AppBar(title=Text("Flet app"), bgcolor=colors.SURFACE_VARIANT),
                    Row(
                        [
                            Column(
                                [
                                    ElevatedButton("日志", on_click=open_log),
                                    ElevatedButton("配置", on_click=open_settings),
                                ],
                            ),
                            VerticalDivider(),
                            ft.Container(
                                # ft.Stack(
                                #     [
                                #         ft.Container(
                                #             width=20,
                                #             height=20,
                                #             bgcolor=ft.colors.RED,
                                #             border_radius=5,
                                #         ),
                                #         ft.Container(
                                #             width=20,
                                #             height=20,
                                #             bgcolor=ft.colors.YELLOW,
                                #             border_radius=5,
                                #             right=0,
                                #         ),
                                #         ft.Container(
                                #             width=20,
                                #             height=20,
                                #             bgcolor=ft.colors.BLUE,
                                #             border_radius=5,
                                #             right=0,
                                #             bottom=0,
                                #         ),
                                #         ft.Container(
                                #             width=20,
                                #             height=20,
                                #             bgcolor=ft.colors.GREEN,
                                #             border_radius=5,
                                #             left=0,
                                #             bottom=0,
                                #         ),
                                #         ft.Column(
                                #             [
                                #                 ft.Container(
                                #                     width=20,
                                #                     height=20,
                                #                     bgcolor=ft.colors.PURPLE,
                                #                     border_radius=5,
                                #                 )
                                #             ],
                                #             left=35,
                                #             top=35,
                                #         ),
                                #     ]
                                # ),
                                border_radius=8,
                                padding=5,
                                width=400,
                                height=300,
                                bgcolor=ft.colors.GREY_100,
                                alignment=ft.alignment.center,
                            ),
                        ]
                    ),
                ],
            )
        )
        if page.route == "/settings" or page.route == "/settings/mail":
            page.views.append(
                View(
                    "/settings",
                    [
                        AppBar(title=Text("Settings"), bgcolor=colors.SURFACE_VARIANT),
                        Text("Settings!", style="bodyMedium"),
                        ElevatedButton("多人一", on_click=open_world_series_settings),
                    ],
                )
            )
        if page.route == "/settings/mail":
            page.views.append(
                View(
                    "/settings/mail",
                    [
                        AppBar(
                            title=Text("Mail Settings"), bgcolor=colors.SURFACE_VARIANT
                        ),
                        Text("Mail settings!"),
                    ],
                )
            )
        if page.route == "/log":
            page.views.append(
                View(
                    "/log",
                    [
                        AppBar(title=Text("日志"), bgcolor=colors.SURFACE_VARIANT),
                        Text("log"),
                    ],
                    scroll=ScrollMode.ALWAYS,
                )
            )
            t = threading.Thread(target=update_log, args=(page,))
            t.start()
        page.update()

    def view_pop(e):
        print("View pop:", e.view)
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    def open_world_series_settings(e):
        page.go("/settings/world_series")

    def open_settings(e):
        page.go("/settings")

    def open_log(e):
        page.go("/log")

    def update_log(page: Page):
        count = 0
        while page.route == "/log":
            time.sleep(0.02)
            count += 1
            view = page.views[-1]
            if view.route == "/log":
                view.controls.append(Text(f"text count = {count}"))
                page.update()

    page.go(page.route)


flet.app(target=main)
