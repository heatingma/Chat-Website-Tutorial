import re
import pypinyin
from pypinyin import pinyin, Style
from django.core.exceptions import ValidationError


def is_chinese(text):
    """
    check if the input text contains chinese
    """
    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    match = pattern.search(text)
    return match is not None


def get_first_pinyin_letter(chinese):
    pinyin = pypinyin.pinyin(chinese[0], style=pypinyin.STYLE_NORMAL)[0][0]
    return pinyin[0].upper()


def convert_size(size):
    KB = 1024
    MB = KB ** 2
    GB = KB ** 3

    if size < KB:
        return f"{size} B"
    elif size < MB:
        return f"{size / KB:.2f} KB"
    elif size < GB:
        return f"{size / MB:.2f} MB"
    else:
        return f"{size / GB:.2f} GB"
    

def validate_file_size(value):
    max_size = 5 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError("File size cannot exceed 5MB.")


def chinese_to_pinyin(input_text):
     pinyin_list = []
     for char in input_text:
         if '\u4e00' <= char <= '\u9fff':
             pinyin_list.extend(pinyin(char, style=Style.NORMAL))
         elif char.isalnum():
             pinyin_list.append([char])

     pinyin_str = ''.join([item[0] for item in pinyin_list])
     return pinyin_str