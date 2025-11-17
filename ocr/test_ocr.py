from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="japan", # 通过 lang 参数指定使用法语的识别模型
    use_doc_orientation_classify=False, # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
    use_doc_unwarping=False, # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
    use_textline_orientation=False, # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
)
result = ocr.predict("./img/jp.png")
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")
    