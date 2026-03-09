cleaned_code = "    C1 --> C1_1[数据频率: 每秒100~1000条]"
import re
cleaned_code = re.sub(r'[，；、。；：、。；：？【】《》""''（）()～~]', '-', cleaned_code)
print(cleaned_code)