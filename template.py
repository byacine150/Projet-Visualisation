'''
    Creates the theme to be used in our bar chart.
'''
import plotly.graph_objects as go
import plotly.io as pio

THEME = {
    'bar_colors': [
        "#AD1F3E",
        "#cc3a41",
        "#e48d3c",
        "#dd4306",
        "#921F2E",
        "#d4b00d"
    ],
    'background_color': "#f0eeda",
    'font_family': 'Montserrat',
    'font_color': "#474545",
    'label_font_size': 16,
    'label_background_color': "#dad8d8"
}


def create_template():
    '''
        Adds a new layout template to pio's templates.

        The template sets the font color and
        font to the values defined above in
        the THEME dictionary.

        The plot background and paper background
        are the background color defined
        above in the THEME dictionary.

        Also, sets the hover label to have a
        background color and font size
        as defined for the label in the THEME dictionary.
        The hover label's font color is the same
        as the theme's overall font color. The hover mode
        is set to 'closest'.

        Also sets the colors for the bars in
        the bar chart to those defined in
        the THEME dictionary.

    '''
    custom_template = go.layout.Template(pio.templates['simple_white'])
    custom_template.layout.update(
        colorway=THEME['bar_colors'],
        plot_bgcolor=THEME['background_color'],
        paper_bgcolor=THEME['background_color'],
        font=dict(
            family=THEME['font_family'],
            color=THEME['font_color']
        ),
    )
    pio.templates['custom'] = custom_template
