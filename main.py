import streamlit as st
from io import BytesIO
from PIL import Image
import warnings
warnings.filterwarnings('ignore')
from utils import *

st.set_page_config(page_title = 'Package optimizer', layout ='wide')

MAX_SLIDER = 20.5
S1 = 4.0
S2 = 6.0
S3 = 10.0
st.markdown('### Check if you can optimize Amazon fees')

with st.expander('Upload your own file'):
    download_button, upload_button = st.columns([1,4])
    buf = create_upload_template()
    download_button.download_button('Download template', file_name='Template.xlsx', data=buf.getvalue())
    if upload_button.file_uploader('Upload your file', key = 'upload_file'):
        result = read_prepare_file(st.session_state.upload_file, st.session_state.limit, st.session_state.limit2, st.session_state.reshape_mode, top_best=5)
        upload_button.download_button('Download result', file_name='Best options.xlsx', data = result.getvalue())


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
dims_col.radio('Select reshape mode', options = ['Sum of lengths','Square'], horizontal = True, key = 'mode', on_change=update_image, help = 'The reshaping will be done either by keeping the sum of lenghts, or the total square of the box')

dims_col.slider('Width, in',0.5, MAX_SLIDER, step = 0.01, key = 's1', value = S3, on_change=update_image, )
dimensions_col.number_input('width', value = st.session_state.s1, on_change=update_slider, key = 'input_width', min_value = 0.01)

dims_col.slider('Height, in',0.5, MAX_SLIDER, step = 0.01, key = 's2', value = S2, on_change=update_image)
dimensions_col.number_input('height', value = st.session_state.s2, on_change=update_slider, key = 'input_height', min_value = 0.01)

dims_col.slider('Depth, in',0.5, MAX_SLIDER, step = 0.01, key = 's3', value = S1, on_change=update_image)
dimensions_col.number_input('depth', value = st.session_state.s3, on_change=update_slider, key = 'input_depth', min_value = 0.01)
dimensions_col.number_input('Product weight, lbs', value = 3.0, on_change=update_image, key = 'weight', step = 0.01, min_value = 0.01)
write_metrics(metrics, button_col, dims = True)

if dims_col.checkbox('Set hard limits to min side (in)', on_change=update_image):
    dimensions_col.number_input('Hard limit', value = default_img.shape[0], key = 'limit', on_change=update_image, label_visibility='hidden', min_value = 0.01)
else:
    st.session_state.limit = 0.5
if dims_col.checkbox('Set hard limits to median side (in)', on_change=update_image):
    dimensions_col.number_input('Hard limit 2', value = default_img.shape[0], key = 'limit2', on_change=update_image, label_visibility='hidden', min_value = 0.01)
else:
    st.session_state.limit2 = 0.5


st.session_state.reshape_mode = 'lengths' if st.session_state.mode == 'Sum of lengths' else 'square'
try:
    variant1, variant2, variant3 = st.session_state['custom_img'].reshape(limit = float(st.session_state.limit), limit2 = float(st.session_state.limit2), mode = st.session_state.reshape_mode)[:3]
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
except Exception:
    st.error(f'Sorry, no available options with these parameters')
