import streamlit as st
import main

st.title("菜品识别&热量测算")
upload_img = st.file_uploader("上传菜品图片",type=["jpg","png"])
if upload_img:
    st.image(upload_img)
    res = main.food_agent_run(upload_img)
    st.write("菜品：",res["name"])
    st.write("食材：",res["material"])
    st.write("热量：",res["cal"],"kcal")
