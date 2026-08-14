from app.api.v1 import widgets_equity, widgets_macro, widgets_news, widgets_options, widgets_portfolio, widgets_og
from app.core.widget_registry import get_widgets
widgets = get_widgets()
print('Total widgets registered:', len(widgets))
for name, config in widgets.items():
    print(f'  - {config["endpoint"]}: {config["name"]} ({config["category"]})')