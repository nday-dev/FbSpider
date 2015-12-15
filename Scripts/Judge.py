#--coding:utf-8--
import re
import json

class Judge():
    def __init__(self, 
            SurnameCharacter = 'Surname.Chinese.json', SurnamePinyin = 'Surname.Pinyin.json'):

        # self.SurnameCharacter = json.load(open(SurnameCharacter, 'rb'))
        self.SurnamePinyin = json.load(open(SurnamePinyin, 'rb'))
        self.Extractor = re.compile(r'^([\w]+)[ ]?.*?[ ]?(?:([\w]*)$)')
        self.NotChineseCharacter = re.compile(ur'^[^\u4e00-\u9fa5]*$')

    def SurnameJudge(self, Name):
        if self.NotChineseCharacter.search(Name) == None: # True if Name contains Chinese Characters.
            return True

        Name = Name.lower()
        Surname = self.Extractor.findall(Name)[0]
        for element in Surname:
            try:
                if self.SurnamePinyin[element]:
                    return True
            except KeyError:
                pass
        return False

    def DescriptionJudge(self, Description):
        if self.NotChineseCharacter.search(Description) == None: # Ture if Description contains Chinese Characters.
            return True

        return False
