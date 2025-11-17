from paddleocr import PaddleOCR
import time
import json
import os

# 全局OCR对象
ocr = PaddleOCR(
    use_doc_orientation_classify=False, # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
    use_doc_unwarping=False, # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
    use_textline_orientation=False, # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
    device="gpu",
    lang="en"
)

def process_image_ocr(image_path: str, output_dir: str = "output") -> str:
    """
    处理图片OCR并返回除第一个单词外的拼接文本
    
    Args:
        image_path (str): 图片路径
        output_dir (str): 输出目录，默认为"output"
        
    Returns:
        str: 除第一个单词外的拼接文本
    """
    start_time = time.time()
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 在OCR处理前，清空输出目录中的所有JSON文件（避免读取旧文件）
    existing_json_files = [f for f in os.listdir(output_dir) if f.endswith(".json")]
    for old_file in existing_json_files:
        try:
            os.remove(os.path.join(output_dir, old_file))
            print(f"已删除旧文件: {old_file}")
        except Exception as e:
            print(f"删除旧文件失败 {old_file}: {e}")
    
    # OCR识别
    result = ocr.predict(image_path)
    
    # 保存JSON文件
    for res in result:
        res.save_to_json(output_dir)
    
    # 只读取刚生成的JSON文件并处理rec_texts
    concatenated_texts = []
    json_files = [f for f in os.listdir(output_dir) if f.endswith(".json")]
    
    for json_file in json_files:
        json_path = os.path.join(output_dir, json_file)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            rec_texts = data.get('rec_texts', [])
            if len(rec_texts) > 1:
                concatenated_text = ' '.join(rec_texts[1:])
                concatenated_texts.append(concatenated_text)
                print(f"处理文件 {json_file} - 除第一个单词外的拼接结果:", concatenated_text)
            else:
                # 如果只有一个单词或没有单词，返回所有内容
                if rec_texts:
                    concatenated_text = ' '.join(rec_texts)
                    concatenated_texts.append(concatenated_text)
                    print(f"处理文件 {json_file} - 完整文本:", concatenated_text)
                else:
                    print(f"处理文件 {json_file} - 未找到文本内容")
            
            # 读取完成后立即删除JSON文件
            os.remove(json_path)
            print(f"已删除处理完的文件: {json_file}")
            
        except Exception as e:
            print(f"处理文件 {json_file} 时出错: {e}")
            # 即使出错也尝试删除文件
            try:
                os.remove(json_path)
            except:
                pass
    
    # 结束计时
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"OCR处理时间: {execution_time:.6f} 秒")
    
    # 返回第一个结果，如果有多个文件则返回第一个
    return concatenated_texts[0] if concatenated_texts else ""

def get_ocr_text_without_first_word(image_path: str) -> str:
    """
    简化版本：直接获取OCR文本（除第一个单词外）
    
    Args:
        image_path (str): 图片路径
        
    Returns:
        str: 除第一个单词外的拼接文本
    """
    return process_image_ocr(image_path)

# 示例调用
if __name__ == "__main__":
    # 方法1：使用详细函数
    image_path = "./img/2.png"
    result_text = process_image_ocr(image_path)
    print(f"\n最终结果: {result_text}")
    
    print("\n" + "="*50 + "\n")
    
    # # 方法2：使用简化函数
    # simple_result = get_ocr_text_without_first_word(image_path)
    # print(f"简化调用结果: {simple_result}")
