




import csv
import json

def extractCharaSettings(charadata):
    charaspecdict = {}
    charaspecdict["api"] = charadata["Voice"]["API"] 
    charaspecdict["styleid"] = charadata["VoiceParameter"]["StyleID"]
    charaspecdict ["speed"] = charadata["VoiceParameter"]["Speed"]
    charaspecdict ["pitch"] = charadata["VoiceParameter"]["Pitch"]
    charaspecdict ["intonation"] = charadata["VoiceParameter"]["Intonation"]
    charaspecdict ["atime"] = charadata["AdditionalTime"]
    charaspecdict ["posx"] = charadata["X"]["Values"][0]["Value"]
    charaspecdict ["posy"] = charadata["Y"]["Values"][0]["Value"]
    charaspecdict ["font"] = charadata["Font"]
    charaspecdict ["fontsize"] = charadata["FontSize"]["Values"][0]["Value"]
    print(charaspecdict)
    return charaspecdict

def getcharadata():
# CSVファイルを開く
    with open('sample.csv', 'r') as c:
        # JSONファイルを開く
        with open('YukkuriMovieMaker.Settings.CharacterSettings.json', 'r', encoding='utf-8-sig') as j:
            reader = csv.reader(c)
            data = json.load(j)
            print('---')

            namedatadict = {}

            # 各行を処理
            for row in reader:
                print(row)

                if row[0] in namedatadict:
                    charadata = namedatadict[row[0]]


                else:
                    for item in data["Characters"]:
                        if item.get('Name') == row[0]:
                            charadata = extractCharaSettings(item)
                            namedatadict[row[0]] = charadata
    
    return charadata