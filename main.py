import streamlit as st
from io import BytesIO
from PIL import Image
from utils import *

st.set_page_config(page_title = 'Package optimizer', layout ='wide')

MAX_SLIDER = 20.5
S1 = 4.0
S2 = 6.0
S3 = 10.0
st.markdown('### Check if you can optimize Amazon fees')
img_area = st.container()
main_img_col, button_col, dims_col, dimensions_col = img_area.columns([2,1,1,1])

options_area = st.container()
option1, option2, option3 = options_area.columns([1,1,1])

def update_image():
    side1 = st.session_state.s1
    side2 = st.session_state.s2
    side3 = st.session_state.s3
    weight = st.session_state.weight
    st.session_state['custom_img'] = Box(side1, side2, side3, weight)

def update_slider():
    st.session_state.s1 = float(st.session_state.input_width)
    st.session_state.s2 = float(st.session_state.input_height)
    st.session_state.s3 = float(st.session_state.input_depth)
    update_image()
    
def write_metrics(metrics, area, dims = False):
    if dims:
        area.markdown(f'Dimensions:\nl: {metrics[3][0]}, w: {metrics[3][1]}, h: {metrics[3][2]}\nweight: {metrics[4]} lbs')
    area.text(f'V (cu_ft): {round(metrics[5],3)}, S(sqft): {metrics[6]}\nDim weight: {metrics[7]}')
    area.text(f'Size tier:\n{metrics[0]}')
    area.text(f"FBA fee:\nJan-Sept: {metrics[1]['Jan-Sept']}\nOct-Dec: {metrics[1]['Oct-Dec']}\nCombined FBA: {metrics[1]['combined']}")
    area.text(f"Storage fee:\nJan-Sept: {metrics[2]['Jan-Sept']}\nOct-Dec: {metrics[2]['Oct-Dec']}\nCombined storage: {metrics[2]['combined']}")

def get_metrics(object):
    return object.size_tier, object.fulfillment_fees, object.storage_fees, object.shape, object.weight, object.cu_ft, object.square, object.dim_weight

if 'custom_img' not in st.session_state:
    default_img = Box(S3, S2, S1)
    metrics = get_metrics(Box(S3, S2, S1))
    st.session_state['custom_img'] = default_img
else:
    default_img = st.session_state['custom_img']
    metrics = get_metrics(st.session_state['custom_img'])

main_img_col.image(default_img.draw())
dims_col.text('Adjust your current package\ndimensions and weight')
dimensions_col.text('Or enter precise dimensions\nin boxes below')
dims_col.radio('Select reshape mode', options = ['Sum of lengths','Square'], horizontal = True, key = 'mode', on_change=update_image)

dims_col.slider('Width, in',0.5, MAX_SLIDER, step = 0.01, key = 's1', value = S3, on_change=update_image)
dimensions_col.text_input('width', value = st.session_state.s1, on_change=update_slider, key = 'input_width')

dims_col.slider('Height, in',0.5, MAX_SLIDER, step = 0.01, key = 's2', value = S2, on_change=update_image)
dimensions_col.text_input('height', value = st.session_state.s2, on_change=update_slider, key = 'input_height')

dims_col.slider('Depth, in',0.5, MAX_SLIDER, step = 0.01, key = 's3', value = S1, on_change=update_image)
dimensions_col.text_input('depth', value = st.session_state.s3, on_change=update_slider, key = 'input_depth')
dimensions_col.text_input('Product weight, lbs', value = '3', on_change=update_image, key = 'weight')
write_metrics(metrics, button_col, dims = True)


if dims_col.checkbox('Set hard limits to min side (in)', on_change=update_image):
    dims_col.text_input('Hard limit', default_img.shape[0], key = 'limit', on_change=update_image, label_visibility='hidden')
else:
    st.session_state.limit = 0
reshape_mode = 'lengths' if st.session_state.mode == 'Sum of lengths' else 'square'
try:
    variant1, variant2, variant3 = st.session_state['custom_img'].reshape(limit = float(st.session_state.limit), mode = reshape_mode)
    option1.text('Option 1')
    option1.image(variant1.draw())
    metrics1 = get_metrics(variant1)
    write_metrics(metrics1, option1, dims = True)

    option2.text('Option 2')
    option2.image(variant2.draw())
    metrics2 = get_metrics(variant2)
    write_metrics(metrics2, option2, dims = True)

    option3.text('Option 3')
    option3.image(variant3.draw())
    metrics3 = get_metrics(variant3)
    write_metrics(metrics3, option3, dims = True)
except Exception as e:
    st.error(f'Sorry, no available options:\n\n{e}')
