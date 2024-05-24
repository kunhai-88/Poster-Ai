import json

def extract_text_elements_with_structure(json_data):
    
    def traverse_elements(elements):
        if elements is None:
            return []
        filtered_elements = []
        for element in elements:
            if isinstance(element, dict):
                new_element = {}
                if 'content' in element and isinstance(element['content'], str):
                    new_element = {
                        'uuid': element.get('uuid', None),
                        'type': element.get('type', None),
                        'content': element['content']
                    }
                    # Process contents if available
                    if 'contents' in element:
                        new_element['contents'] = traverse_elements(element['contents'])
                if 'elements' in element:
                    new_element['elements'] = traverse_elements(element['elements'])
                
                filtered_elements.append(new_element)
            elif isinstance(element, list):
                filtered_elements.extend(traverse_elements(element))
        return filtered_elements

    if 'layouts' in json_data:
        json_data['layouts'] = traverse_elements(json_data['layouts'])
    data = {}
    data['layouts'] = json_data['layouts']
    return data

def merge_text_elements_with_structure(original_data, modified_data):
    def update_elements(original_elements, modified_elements):
        if not original_elements or not modified_elements:
            return
        
        for original_element, modified_element in zip(original_elements, modified_elements):
            if isinstance(original_element, dict) and isinstance(modified_element, dict):
                if 'content' in original_element and 'content' in modified_element:
                    # print(modified_element)
                    original_element['content'] = modified_element['content']
                if 'elements' in original_element and 'elements' in modified_element:
                    update_elements(original_element['elements'], modified_element['elements'])
                if 'contents' in original_element and 'contents' in modified_element:
                    update_elements(original_element['contents'], modified_element['contents'])

    if 'layouts' in original_data and 'layouts' in modified_data:
        update_elements(original_data['layouts'], modified_data['layouts'])
    return original_data

# 读取JSON布局文件
layout_file = 'layout.json'  # 替换为你的文件路径
with open(layout_file, 'r') as file:
    layout_data = json.load(file)
    
#data = extract_text_elements_with_structure(layout_data)

# # 将data写入到文件中
# with open('text_elements.json', 'w') as file:
#     json.dump(data, file, indent=4,ensure_ascii=False)

data_file = 'text_elements.json'  # 替换为你的文件路径
with open(data_file, 'r') as file:
    data = json.load(file)
    
final_data = merge_text_elements_with_structure(layout_data, data)
with open('text_final.json', 'w') as file:
    json.dump(final_data, file, indent=4,ensure_ascii=False)
