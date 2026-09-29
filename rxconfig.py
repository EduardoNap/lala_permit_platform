import reflex as rx

config = rx.Config(
    app_name="prueba",
    favicon="company-logo.png",
    show_built_with_reflex=False,
    api_url="https://frogh.net",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)
