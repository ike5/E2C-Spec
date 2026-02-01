#!/usr/bin/env python3
"""
Simple English-to-Chinese Input Method
- Type English words to see Chinese translation candidates
- Select with numbers
- Frequency rankings update based on your selections
"""

import json
import os
from pathlib import Path

# Default dictionary: English -> list of (Chinese, base_frequency) tuples
# Higher frequency = more common/preferred
DEFAULT_DICTIONARY = {
    # Greetings
    "hello": [("你好", 100), ("您好", 80), ("喂", 60)],
    "hi": [("嗨", 100), ("你好", 90)],
    "goodbye": [("再见", 100), ("拜拜", 90), ("告辞", 50)],
    "bye": [("拜拜", 100), ("再见", 90)],
    "thanks": [("谢谢", 100), ("感谢", 80), ("多谢", 70)],
    "sorry": [("对不起", 100), ("抱歉", 90), ("不好意思", 85)],
    "please": [("请", 100), ("拜托", 70)],
    "welcome": [("欢迎", 100), ("不客气", 80)],

    # Pronouns
    "i": [("我", 100)],
    "you": [("你", 100), ("您", 80), ("你们", 60)],
    "he": [("他", 100)],
    "she": [("她", 100)],
    "it": [("它", 100), ("这", 60)],
    "we": [("我们", 100), ("咱们", 80)],
    "they": [("他们", 100), ("她们", 80), ("它们", 60)],
    "this": [("这", 100), ("这个", 90)],
    "that": [("那", 100), ("那个", 90)],
    "what": [("什么", 100), ("何", 50)],
    "who": [("谁", 100)],
    "where": [("哪里", 100), ("哪儿", 90), ("何处", 50)],
    "when": [("什么时候", 100), ("何时", 70)],
    "why": [("为什么", 100), ("为何", 60)],
    "how": [("怎么", 100), ("如何", 80), ("怎样", 70)],

    # Common verbs
    "be": [("是", 100), ("在", 80)],
    "is": [("是", 100), ("在", 80)],
    "am": [("是", 100), ("在", 80)],
    "are": [("是", 100), ("在", 80)],
    "have": [("有", 100), ("拥有", 70)],
    "has": [("有", 100)],
    "do": [("做", 100), ("干", 70)],
    "go": [("去", 100), ("走", 80)],
    "come": [("来", 100)],
    "see": [("看", 100), ("见", 90), ("看见", 85)],
    "look": [("看", 100), ("瞧", 60)],
    "want": [("想", 100), ("要", 95), ("想要", 90)],
    "need": [("需要", 100), ("要", 80)],
    "know": [("知道", 100), ("认识", 80), ("了解", 70)],
    "think": [("想", 100), ("认为", 90), ("觉得", 85)],
    "say": [("说", 100), ("讲", 70)],
    "speak": [("说", 100), ("讲", 80), ("说话", 75)],
    "tell": [("告诉", 100), ("说", 70)],
    "ask": [("问", 100), ("请求", 60)],
    "give": [("给", 100), ("送", 70)],
    "take": [("拿", 100), ("取", 80), ("带", 75)],
    "get": [("得到", 100), ("获得", 90), ("拿", 70)],
    "make": [("做", 100), ("制作", 80), ("使", 70)],
    "let": [("让", 100), ("允许", 60)],
    "put": [("放", 100), ("放置", 70)],
    "use": [("用", 100), ("使用", 90)],
    "find": [("找", 100), ("发现", 90), ("找到", 85)],
    "try": [("试", 100), ("尝试", 90), ("试试", 85)],
    "leave": [("离开", 100), ("走", 70), ("留下", 60)],
    "call": [("叫", 100), ("打电话", 90), ("称呼", 70)],
    "feel": [("感觉", 100), ("觉得", 90), ("感到", 80)],
    "become": [("成为", 100), ("变成", 90)],
    "begin": [("开始", 100), ("开头", 60)],
    "start": [("开始", 100), ("启动", 70)],
    "stop": [("停", 100), ("停止", 95), ("别", 60)],
    "help": [("帮助", 100), ("帮", 95), ("帮忙", 90)],
    "work": [("工作", 100), ("干活", 60)],
    "play": [("玩", 100), ("玩耍", 70), ("播放", 60)],
    "run": [("跑", 100), ("运行", 70)],
    "walk": [("走", 100), ("走路", 90), ("散步", 70)],
    "eat": [("吃", 100), ("吃饭", 80)],
    "drink": [("喝", 100), ("饮", 50)],
    "sleep": [("睡", 100), ("睡觉", 95)],
    "live": [("住", 100), ("生活", 90), ("活", 70)],
    "die": [("死", 100), ("去世", 80)],
    "buy": [("买", 100), ("购买", 80)],
    "sell": [("卖", 100), ("出售", 70)],
    "pay": [("付", 100), ("付钱", 90), ("支付", 85)],
    "open": [("开", 100), ("打开", 95)],
    "close": [("关", 100), ("关闭", 90), ("关上", 85)],
    "read": [("读", 100), ("看", 90), ("阅读", 80)],
    "write": [("写", 100), ("书写", 60)],
    "learn": [("学", 100), ("学习", 95)],
    "teach": [("教", 100), ("教书", 70)],
    "study": [("学习", 100), ("研究", 80)],
    "like": [("喜欢", 100), ("爱", 70)],
    "love": [("爱", 100), ("喜爱", 80), ("热爱", 70)],
    "hate": [("恨", 100), ("讨厌", 90)],
    "wait": [("等", 100), ("等待", 90)],
    "remember": [("记得", 100), ("记住", 90), ("记", 80)],
    "forget": [("忘", 100), ("忘记", 95)],
    "understand": [("懂", 100), ("理解", 90), ("明白", 85)],
    "believe": [("相信", 100), ("信", 70)],
    "hope": [("希望", 100), ("盼望", 60)],
    "wish": [("希望", 100), ("祝", 80), ("愿望", 60)],
    "meet": [("见", 100), ("见面", 95), ("遇见", 80)],
    "send": [("送", 100), ("发送", 90), ("寄", 80)],
    "receive": [("收到", 100), ("收", 90), ("接收", 80)],
    "bring": [("带", 100), ("带来", 90), ("拿来", 80)],
    "carry": [("拿", 100), ("带", 90), ("搬", 70)],
    "hold": [("拿", 100), ("握", 90), ("抱", 80)],
    "stand": [("站", 100), ("站立", 80)],
    "sit": [("坐", 100)],
    "lie": [("躺", 100), ("说谎", 70)],
    "rise": [("升", 100), ("起来", 90), ("上升", 80)],
    "fall": [("落", 100), ("掉", 90), ("摔", 80)],
    "grow": [("长", 100), ("成长", 90), ("生长", 80)],
    "cut": [("切", 100), ("剪", 90)],
    "break": [("打破", 100), ("破", 90), ("打断", 70)],
    "build": [("建", 100), ("建造", 90), ("建设", 80)],
    "drive": [("开车", 100), ("开", 90), ("驾驶", 80)],
    "fly": [("飞", 100)],
    "swim": [("游泳", 100), ("游", 90)],
    "sing": [("唱", 100), ("唱歌", 95)],
    "dance": [("跳舞", 100), ("舞蹈", 60)],
    "draw": [("画", 100), ("绘画", 70)],
    "cook": [("做饭", 100), ("煮", 80), ("烹饪", 70)],
    "clean": [("清洁", 100), ("打扫", 90), ("干净", 70)],
    "wash": [("洗", 100)],
    "wear": [("穿", 100), ("戴", 80)],
    "win": [("赢", 100), ("获胜", 80)],
    "lose": [("输", 100), ("丢失", 80), ("失去", 75)],
    "change": [("变", 100), ("改变", 95), ("换", 80)],
    "move": [("动", 100), ("移动", 90), ("搬", 70)],
    "turn": [("转", 100), ("转动", 80), ("变成", 70)],
    "show": [("展示", 100), ("给看", 80), ("表演", 70)],
    "hide": [("藏", 100), ("隐藏", 90)],
    "follow": [("跟", 100), ("跟随", 90), ("关注", 70)],
    "enter": [("进入", 100), ("进", 95)],
    "exit": [("出去", 100), ("退出", 90)],
    "return": [("回来", 100), ("返回", 95), ("回", 90)],
    "answer": [("回答", 100), ("答", 80)],
    "finish": [("完成", 100), ("结束", 90), ("做完", 80)],
    "continue": [("继续", 100)],
    "choose": [("选", 100), ("选择", 95)],
    "decide": [("决定", 100)],
    "save": [("保存", 100), ("救", 80), ("省", 70)],
    "spend": [("花", 100), ("花费", 90)],
    "keep": [("保持", 100), ("留", 80), ("保留", 75)],
    "pass": [("过", 100), ("通过", 90), ("传", 70)],
    "add": [("加", 100), ("添加", 90)],
    "check": [("检查", 100), ("查", 90)],
    "fix": [("修理", 100), ("修", 95), ("修复", 90)],
    "prepare": [("准备", 100), ("预备", 60)],
    "fill": [("填", 100), ("装满", 80)],
    "share": [("分享", 100), ("共享", 80)],
    "join": [("加入", 100), ("参加", 90)],
    "create": [("创建", 100), ("创造", 90)],
    "develop": [("发展", 100), ("开发", 90)],
    "support": [("支持", 100)],
    "include": [("包括", 100), ("包含", 90)],
    "set": [("设置", 100), ("设定", 80)],
    "describe": [("描述", 100), ("形容", 80)],
    "explain": [("解释", 100), ("说明", 90)],
    "happen": [("发生", 100)],
    "allow": [("允许", 100), ("让", 80)],
    "accept": [("接受", 100), ("同意", 70)],
    "refuse": [("拒绝", 100)],
    "agree": [("同意", 100)],
    "require": [("需要", 100), ("要求", 90)],
    "achieve": [("达到", 100), ("实现", 95), ("取得", 90)],

    # Common nouns
    "person": [("人", 100), ("人物", 60)],
    "people": [("人", 100), ("人们", 95), ("人民", 70)],
    "man": [("男人", 100), ("人", 70)],
    "woman": [("女人", 100), ("女性", 80)],
    "child": [("孩子", 100), ("儿童", 80), ("小孩", 75)],
    "boy": [("男孩", 100)],
    "girl": [("女孩", 100)],
    "baby": [("宝宝", 100), ("婴儿", 90)],
    "friend": [("朋友", 100)],
    "family": [("家庭", 100), ("家人", 95), ("家", 80)],
    "father": [("父亲", 100), ("爸爸", 95), ("爹", 60)],
    "mother": [("母亲", 100), ("妈妈", 95), ("娘", 50)],
    "dad": [("爸爸", 100), ("爸", 90)],
    "mom": [("妈妈", 100), ("妈", 90)],
    "brother": [("兄弟", 100), ("哥哥", 90), ("弟弟", 85)],
    "sister": [("姐妹", 100), ("姐姐", 90), ("妹妹", 85)],
    "son": [("儿子", 100)],
    "daughter": [("女儿", 100)],
    "husband": [("丈夫", 100), ("老公", 90)],
    "wife": [("妻子", 100), ("老婆", 90)],
    "teacher": [("老师", 100), ("教师", 80)],
    "student": [("学生", 100)],
    "doctor": [("医生", 100), ("大夫", 70)],
    "name": [("名字", 100), ("名", 80)],
    "home": [("家", 100)],
    "house": [("房子", 100), ("房屋", 70)],
    "room": [("房间", 100), ("屋子", 70)],
    "door": [("门", 100)],
    "window": [("窗户", 100), ("窗", 90)],
    "table": [("桌子", 100), ("桌", 90)],
    "chair": [("椅子", 100)],
    "bed": [("床", 100)],
    "food": [("食物", 100), ("吃的", 80)],
    "water": [("水", 100)],
    "rice": [("米饭", 100), ("米", 80)],
    "tea": [("茶", 100)],
    "coffee": [("咖啡", 100)],
    "meat": [("肉", 100)],
    "fish": [("鱼", 100)],
    "egg": [("鸡蛋", 100), ("蛋", 90)],
    "fruit": [("水果", 100)],
    "apple": [("苹果", 100)],
    "book": [("书", 100), ("书籍", 70)],
    "pen": [("笔", 100), ("钢笔", 70)],
    "paper": [("纸", 100)],
    "word": [("字", 100), ("词", 90), ("单词", 80)],
    "letter": [("信", 100), ("字母", 80)],
    "number": [("数字", 100), ("号码", 80), ("数", 70)],
    "money": [("钱", 100), ("金钱", 60)],
    "time": [("时间", 100), ("时候", 80)],
    "day": [("天", 100), ("日", 80)],
    "night": [("夜", 100), ("晚上", 95), ("夜晚", 80)],
    "morning": [("早上", 100), ("上午", 90), ("早晨", 80)],
    "afternoon": [("下午", 100)],
    "evening": [("晚上", 100), ("傍晚", 80)],
    "week": [("周", 100), ("星期", 95), ("礼拜", 70)],
    "month": [("月", 100), ("月份", 80)],
    "year": [("年", 100)],
    "today": [("今天", 100)],
    "tomorrow": [("明天", 100)],
    "yesterday": [("昨天", 100)],
    "now": [("现在", 100), ("如今", 60)],
    "thing": [("东西", 100), ("事情", 90), ("事", 80)],
    "place": [("地方", 100), ("地点", 80)],
    "way": [("路", 100), ("方法", 90), ("方式", 80)],
    "world": [("世界", 100), ("天下", 50)],
    "country": [("国家", 100), ("国", 90)],
    "city": [("城市", 100)],
    "street": [("街", 100), ("街道", 90)],
    "road": [("路", 100), ("道路", 80)],
    "car": [("车", 100), ("汽车", 90)],
    "bus": [("公交车", 100), ("巴士", 80)],
    "train": [("火车", 100), ("列车", 70)],
    "plane": [("飞机", 100)],
    "phone": [("电话", 100), ("手机", 95)],
    "computer": [("电脑", 100), ("计算机", 80)],
    "internet": [("互联网", 100), ("网络", 90)],
    "weather": [("天气", 100)],
    "sun": [("太阳", 100), ("阳光", 70)],
    "moon": [("月亮", 100), ("月", 80)],
    "star": [("星星", 100), ("星", 90)],
    "sky": [("天空", 100), ("天", 90)],
    "rain": [("雨", 100), ("下雨", 80)],
    "snow": [("雪", 100), ("下雪", 80)],
    "wind": [("风", 100)],
    "tree": [("树", 100)],
    "flower": [("花", 100)],
    "grass": [("草", 100)],
    "dog": [("狗", 100)],
    "cat": [("猫", 100)],
    "bird": [("鸟", 100)],
    "color": [("颜色", 100), ("色", 70)],
    "red": [("红", 100), ("红色", 95)],
    "blue": [("蓝", 100), ("蓝色", 95)],
    "green": [("绿", 100), ("绿色", 95)],
    "yellow": [("黄", 100), ("黄色", 95)],
    "white": [("白", 100), ("白色", 95)],
    "black": [("黑", 100), ("黑色", 95)],
    "big": [("大", 100)],
    "small": [("小", 100)],
    "long": [("长", 100)],
    "short": [("短", 100), ("矮", 70)],
    "high": [("高", 100)],
    "low": [("低", 100)],
    "new": [("新", 100)],
    "old": [("老", 100), ("旧", 80)],
    "good": [("好", 100), ("良好", 70)],
    "bad": [("坏", 100), ("不好", 80)],
    "right": [("对", 100), ("右", 80), ("正确", 75)],
    "wrong": [("错", 100), ("不对", 80)],
    "left": [("左", 100), ("剩下", 60)],
    "fast": [("快", 100)],
    "slow": [("慢", 100)],
    "easy": [("容易", 100), ("简单", 95)],
    "hard": [("难", 100), ("困难", 90), ("硬", 60)],
    "hot": [("热", 100)],
    "cold": [("冷", 100)],
    "warm": [("温暖", 100), ("暖和", 90)],
    "cool": [("凉", 100), ("凉快", 90), ("酷", 60)],
    "beautiful": [("美丽", 100), ("漂亮", 95), ("美", 80)],
    "happy": [("高兴", 100), ("快乐", 95), ("开心", 90)],
    "sad": [("难过", 100), ("伤心", 95), ("悲伤", 80)],
    "angry": [("生气", 100), ("愤怒", 80)],
    "afraid": [("害怕", 100), ("怕", 90)],
    "hungry": [("饿", 100)],
    "thirsty": [("渴", 100)],
    "tired": [("累", 100), ("疲惫", 70)],
    "busy": [("忙", 100), ("忙碌", 80)],
    "free": [("自由", 100), ("免费", 90), ("空闲", 70)],
    "same": [("一样", 100), ("相同", 90)],
    "different": [("不同", 100), ("不一样", 95)],
    "important": [("重要", 100)],
    "possible": [("可能", 100)],
    "true": [("真", 100), ("真的", 95), ("真实", 80)],
    "false": [("假", 100), ("错误", 80)],
    "every": [("每", 100)],
    "all": [("所有", 100), ("全部", 95), ("都", 80)],
    "some": [("一些", 100), ("有些", 90)],
    "many": [("很多", 100), ("许多", 95)],
    "few": [("少", 100), ("几个", 80)],
    "much": [("很多", 100), ("多", 90)],
    "more": [("更多", 100), ("更", 80)],
    "most": [("最", 100), ("大多数", 80)],
    "other": [("其他", 100), ("别的", 90)],
    "another": [("另一个", 100), ("另外", 80)],
    "first": [("第一", 100), ("首先", 80)],
    "last": [("最后", 100), ("上一个", 70)],
    "next": [("下一个", 100), ("下次", 80)],
    "only": [("只", 100), ("只有", 95), ("唯一", 70)],
    "also": [("也", 100), ("还", 90)],
    "very": [("很", 100), ("非常", 95)],
    "too": [("太", 100), ("也", 80)],
    "really": [("真的", 100), ("确实", 80)],
    "just": [("只是", 100), ("刚刚", 80), ("刚才", 75)],
    "already": [("已经", 100)],
    "still": [("还", 100), ("仍然", 90)],
    "again": [("再", 100), ("又", 90)],
    "always": [("总是", 100), ("一直", 90)],
    "never": [("从不", 100), ("从来不", 90)],
    "often": [("经常", 100), ("常常", 95)],
    "sometimes": [("有时候", 100), ("有时", 95)],
    "usually": [("通常", 100), ("一般", 80)],
    "maybe": [("可能", 100), ("也许", 95), ("或许", 80)],
    "yes": [("是", 100), ("是的", 95), ("对", 80)],
    "no": [("不", 100), ("没有", 80), ("不是", 75)],
    "not": [("不", 100), ("没", 90)],
    "and": [("和", 100), ("与", 80), ("并且", 70)],
    "or": [("或", 100), ("或者", 95)],
    "but": [("但是", 100), ("但", 95), ("可是", 80)],
    "if": [("如果", 100), ("假如", 70)],
    "because": [("因为", 100)],
    "so": [("所以", 100), ("因此", 80)],
    "then": [("然后", 100), ("那么", 80)],
    "when": [("当", 100), ("什么时候", 80)],
    "while": [("当", 100), ("而", 80)],
    "before": [("之前", 100), ("以前", 90)],
    "after": [("之后", 100), ("以后", 90)],
    "about": [("关于", 100), ("大约", 80)],
    "with": [("和", 100), ("跟", 90), ("用", 70)],
    "without": [("没有", 100), ("无", 70)],
    "for": [("为", 100), ("给", 80), ("为了", 75)],
    "from": [("从", 100)],
    "to": [("到", 100), ("向", 80), ("去", 70)],
    "in": [("在", 100), ("里", 80)],
    "on": [("在", 100), ("上", 90)],
    "at": [("在", 100)],
    "of": [("的", 100)],
    "up": [("上", 100)],
    "down": [("下", 100)],
    "here": [("这里", 100), ("这儿", 90)],
    "there": [("那里", 100), ("那儿", 90)],
    "near": [("近", 100), ("附近", 90)],
    "far": [("远", 100)],
    "between": [("之间", 100), ("中间", 80)],
    "through": [("通过", 100), ("穿过", 80)],
    "during": [("在...期间", 100), ("期间", 90)],
    "until": [("直到", 100)],
    "like": [("像", 100), ("喜欢", 90)],
    "than": [("比", 100)],
    "as": [("作为", 100), ("像", 80)],

    # Numbers
    "zero": [("零", 100)],
    "one": [("一", 100)],
    "two": [("二", 100), ("两", 90)],
    "three": [("三", 100)],
    "four": [("四", 100)],
    "five": [("五", 100)],
    "six": [("六", 100)],
    "seven": [("七", 100)],
    "eight": [("八", 100)],
    "nine": [("九", 100)],
    "ten": [("十", 100)],
    "hundred": [("百", 100)],
    "thousand": [("千", 100)],
    "million": [("百万", 100)],

    # Technology & Modern
    "email": [("邮件", 100), ("电子邮件", 90)],
    "message": [("消息", 100), ("信息", 90)],
    "photo": [("照片", 100), ("相片", 80)],
    "video": [("视频", 100)],
    "music": [("音乐", 100)],
    "game": [("游戏", 100)],
    "movie": [("电影", 100)],
    "news": [("新闻", 100)],
    "website": [("网站", 100)],
    "app": [("应用", 100), ("软件", 80)],
    "password": [("密码", 100)],
    "download": [("下载", 100)],
    "upload": [("上传", 100)],
    "search": [("搜索", 100), ("查找", 80)],
    "click": [("点击", 100)],

    # Common expressions
    "ok": [("好", 100), ("行", 90), ("可以", 85)],
    "okay": [("好", 100), ("行", 90), ("可以", 85)],
    "sure": [("当然", 100), ("确定", 80)],
    "maybe": [("可能", 100), ("也许", 95)],
    "well": [("好", 100), ("嗯", 80)],
    "oh": [("哦", 100), ("噢", 80)],
    "wow": [("哇", 100)],
    "oops": [("哎呀", 100)],
}


class EnglishChineseIME:
    def __init__(self, data_file="ime_data.json"):
        self.data_file = Path(data_file)
        self.dictionary = {}
        self.user_frequencies = {}
        self.load_data()

    def load_data(self):
        """Load dictionary and user frequency data."""
        # Start with default dictionary
        self.dictionary = {k: list(v) for k, v in DEFAULT_DICTIONARY.items()}

        # Load user frequencies if file exists
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.user_frequencies = json.load(f)
                print(f"Loaded user preferences from {self.data_file}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load user data: {e}")
                self.user_frequencies = {}
        else:
            self.user_frequencies = {}

    def save_data(self):
        """Save user frequency data to file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_frequencies, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Warning: Could not save user data: {e}")

    def get_candidates(self, english_word):
        """Get Chinese candidates for an English word, sorted by combined frequency."""
        english_word = english_word.lower().strip()

        if english_word not in self.dictionary:
            return []

        candidates = self.dictionary[english_word]

        # Calculate combined frequency (base + user boost)
        def get_score(item):
            chinese, base_freq = item
            user_key = f"{english_word}:{chinese}"
            user_boost = self.user_frequencies.get(user_key, 0)
            return base_freq + user_boost * 10  # User selections have 10x weight

        # Sort by combined frequency (descending)
        sorted_candidates = sorted(candidates, key=get_score, reverse=True)
        return sorted_candidates

    def update_frequency(self, english_word, chinese_char):
        """Update user frequency for a selection."""
        user_key = f"{english_word}:{chinese_char}"
        self.user_frequencies[user_key] = self.user_frequencies.get(user_key, 0) + 1
        self.save_data()

    def lookup(self, english_word):
        """Look up an English word and let user select a Chinese translation."""
        candidates = self.get_candidates(english_word)

        if not candidates:
            print(f"  No translation found for '{english_word}'")
            return None

        # Display candidates
        print(f"\n  Candidates for '{english_word}':")
        for i, (chinese, freq) in enumerate(candidates, 1):
            user_key = f"{english_word}:{chinese}"
            user_count = self.user_frequencies.get(user_key, 0)
            user_info = f" (+{user_count})" if user_count > 0 else ""
            print(f"    {i}. {chinese}{user_info}")

        # Get user selection
        while True:
            try:
                choice = input(f"  Select [1-{len(candidates)}] or 0 to cancel: ").strip()
                if choice == '0' or choice == '':
                    return None

                idx = int(choice) - 1
                if 0 <= idx < len(candidates):
                    selected_chinese = candidates[idx][0]
                    self.update_frequency(english_word, selected_chinese)
                    return selected_chinese
                else:
                    print(f"  Please enter a number between 1 and {len(candidates)}")
            except ValueError:
                print("  Please enter a valid number")

    def run(self):
        """Main loop for the IME."""
        print("=" * 50)
        print("  English-to-Chinese Input Method")
        print("=" * 50)
        print("  Type an English word to see Chinese translations")
        print("  Commands:")
        print("    :q or :quit  - Exit the program")
        print("    :clear       - Clear user frequency data")
        print("    :stats       - Show selection statistics")
        print("    :list        - List all available words")
        print("=" * 50)

        output_buffer = []

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith(':'):
                    cmd = user_input.lower()

                    if cmd in [':q', ':quit', ':exit']:
                        print("\n  Final output:", ''.join(output_buffer) if output_buffer else "(empty)")
                        print("  Goodbye! 再见!")
                        break

                    elif cmd == ':clear':
                        self.user_frequencies = {}
                        self.save_data()
                        print("  User frequency data cleared.")

                    elif cmd == ':stats':
                        if self.user_frequencies:
                            print("\n  Your selection statistics:")
                            sorted_stats = sorted(
                                self.user_frequencies.items(),
                                key=lambda x: x[1],
                                reverse=True
                            )
                            for key, count in sorted_stats[:20]:
                                eng, chn = key.split(':', 1)
                                print(f"    {eng} → {chn}: {count} times")
                        else:
                            print("  No selection history yet.")

                    elif cmd == ':list':
                        words = sorted(self.dictionary.keys())
                        print(f"\n  Available words ({len(words)} total):")
                        # Print in columns
                        cols = 5
                        for i in range(0, len(words), cols):
                            row = words[i:i + cols]
                            print("    " + "  ".join(f"{w:<12}" for w in row))

                    elif cmd == ':output':
                        print("  Current output:", ''.join(output_buffer) if output_buffer else "(empty)")

                    elif cmd == ':reset':
                        output_buffer = []
                        print("  Output buffer cleared.")

                    else:
                        print(f"  Unknown command: {user_input}")

                    continue

                # Look up the word
                result = self.lookup(user_input)

                if result:
                    output_buffer.append(result)
                    print(f"\n  → {result}")
                    print(f"  Current output: {''.join(output_buffer)}")

            except KeyboardInterrupt:
                print("\n\n  Final output:", ''.join(output_buffer) if output_buffer else "(empty)")
                print("  Goodbye! 再见!")
                break
            except EOFError:
                break


def main():
    import sys

    # Allow custom data file path
    data_file = sys.argv[1] if len(sys.argv) > 1 else "ime_data.json"

    ime = EnglishChineseIME(data_file)
    ime.run()


if __name__ == "__main__":
    main()
