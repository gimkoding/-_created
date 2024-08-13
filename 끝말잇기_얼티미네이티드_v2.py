import random                                                # 기본 모듈
from selenium import webdriver                               # pip install selenium
from selenium.webdriver.common.by import By                  # pip install selenium
from hangul_utils import split_syllables, join_jamos         # pip install hangul-utils
import time

print('\n\n-------------------------')
print('⭐ 끝말잇기 봇 V. 2.0 ⭐')
print('-------------------------')
time.sleep(0.5)
print('made by. developers\n')
time.sleep(0.5)

word_lst = [] # 끝말잇기 단어 리스트
worded = []   # 이미 말한 단어 리스트

with open("words_list_kor.txt", "r", encoding='utf-8') as file: # txt 파일에서 단어 불러오기
    for w in file:
        word_lst.append(w.strip())

def check(word): # 네이버 사전을 이용하여 존재하는 단어인지 확인
    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)  # chromedriver 경로 제거
    url = f'https://ko.dict.naver.com/#/search?query={word}&range=all&autoConvert=false'
    driver.get(url)
    driver.implicitly_wait(1)
    xpath = '//*[@id="searchPage_entry"]/div/div[1]/div[1]/a/strong'
    xpath2 = '//*[@id="searchPage_entry"]/div/div[1]/div[1]/span[1]'
    
    global kor
    kor = False
    try:
        voca = driver.find_element(By.XPATH, xpath).text
        
        try:
            iskor = driver.find_element(By.XPATH, xpath2)
            lang = iskor.get_attribute("lang")
            
            if lang == "zh_CN":
                kor = True
        except Exception:
            kor = True
        
        if word == voca:
            return [1, kor]
        else:
            return [-1]
    except Exception:
        return [-1]
    finally:
        driver.quit()  # 드라이버 종료

def korean_divide(korean_word): # 단어를 자음 모음으로 나눔
    # 초성 리스트. 00 ~ 18
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    # 중성 리스트. 00 ~ 20
    JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    # 종성 리스트. 00 ~ 27 + 1(1개 없음)
    JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    
    r_lst = []
    for w in list(korean_word.strip()):
        ## 영어인 경우 구분해서 작성함. 
        if '가'<=w<='힣':
            ## 588개 마다 초성이 바뀜. 
            ch1 = (ord(w) - ord('가'))//588
            ## 중성은 총 28가지 종류
            ch2 = ((ord(w) - ord('가')) - (588*ch1)) // 28
            ch3 = (ord(w) - ord('가')) - (588*ch1) - 28*ch2
            r_lst.append([CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], JONGSUNG_LIST[ch3]])
        else:
            r_lst.append([w])
    return r_lst

def korean_combination(word): # 자음 모음을 단어로 만듬
    char = ''.join(word)
    jamo = split_syllables(char)
    chars = list(set(jamo))
    char_to_ix = { ch:i for i,ch in enumerate(chars) }
    ix_to_char = { i:ch for i,ch in enumerate(chars) }
    jamo_numbers = [char_to_ix[x] for x in jamo]
    restored_jamo = ''.join([ix_to_char[x] for x in jamo_numbers])
    restored_text = join_jamos(restored_jamo)
    return restored_text

def find_start_word(char): # 두음 법칙 적용
    canStart = [list(char)[-1]]
    word = korean_divide(char)
    ch = word[-1][0]
    case = []
    if ch == "ㄹ":
        case.append("ㅇ")
        case.append("ㄴ")
    elif ch == "ㄴ":
        case.append("ㅇ")

    for c in case:
        word[-1][0] = c
        canStart.append(korean_combination(word[-1]))
    return canStart

def is_korean(word): # 완전한 한국어 단어인지 판별
    chars = list(word)
    for c in chars:
        if '가' <= c <= '힣':
            pass
        else:
            return -1
    return 1

def itCan(word, start): # 가능한 단어인지 판별
    for s in start:
        it = word.startswith(s)
        if it:
            return True
    return False

def game(answer, word_lst): # 게임
    global worded
    
    worded.append(answer)
    
    if not word_lst: # 리스트가 비어있는지 확인
        print("리스트가 비어있습니다..ㅠㅠ")
        return -1
    
    start_word = find_start_word(answer)
    
    filtered_words = [word for word in word_lst if itCan(word, start_word) and word not in worded] # AI가 말할 수 있는 단어
    
    if not filtered_words: # AI가 더이상 말할 수 있는 단어가 없는지 확인
        print("\u001b[33m\n컴퓨터는 더 이상 사용할 수 있는 단어가 없습니다.")
        return 1
    
    var = random.choice(filtered_words) # AI가 말할 수 있는 단어 중 한가지를 무작위로 골라 출력
    start_word = find_start_word(var)
    start_word_str = start_word[0]
    for i in range(1, len(start_word)):
        start_word_str += ", "
        start_word_str += start_word[i].replace(" " , "")
    
    print('\u001b[96m' + '\n->', var) # 출력
    print(f'이어질 단어는 {start_word_str}(으)로 시작해야합니다.')
    print('\u001b[37m' + '')
    worded.append(var) # 더이상 말 할 수 없게 worded에 단어 추가

    print('사용자의 차례입니다. 입력해주세요. (-기권: q)')
    answer = input(('\u001b[33m' + '\n-입력: ')) # 단어 입력 받기
    print('\u001b[37m' + '')
    
    if answer == 'q': # 기권
        print('\u001b[31m' + '-허접한 당신은 경기에서 졌습니다.')
        print('\u001b[37m' + '')
        return -1

    while True:
        if answer == 'q': # 기권
            print('\u001b[31m' + '-허접한 당신은 경기에서 졌습니다.')
            print('\u001b[37m' + '')
            return -1
        isKor = is_korean(answer) # 한국어 여부
        if isKor == 1:
            if len(answer) >= 2: # 단어 길이
                check_answer = check(answer) # 표준어 탐색기 작동
                if check_answer[0] == 1:
                    if answer not in worded:
                        if itCan(answer, start_word): # 가능한 단어인지 판별
                            game(answer, word_lst)
                            break
                        else:
                            print('\u001b[\n 31m이어져야 할 단어는', var, '입니다.')
                            print(f'\u001b[31m이어질 단어는 {start_word_str}(으)로 시작해야합니다.')
                            print('\u001b[37m' + '')
                    else:
                        print('\u001b[31m' + '\n이미 사용한 단어입니다. 다시 입력해주세요.')
                        print('\u001b[37m' + '')
                else:
                    print('\u001b[31m' + '\n네이버 사전에 없는 단어입니다. 다시 입력해주세요.')
                    print('\u001b[37m' + '')
            else:
                print('\u001b[31m' + '\n2글자 이상의 단어여야 합니다. 다시 입력해주세요.')
                print('\u001b[37m' + '')
        else:
            print('\u001b[31m' + '\n완전한 한국어 단어만 입력 가능합니다. 다시 입력해주세요.')
            print('\u001b[37m' + '')
        answer = input(('\u001b[33m' + '\n-입력: '))
        print('\u001b[37m' + '')
    if answer == 'q': # 기권
        print('\u001b[31m' + '-\n허접한 당신은 경기에서 졌습니다.')
        print('\u001b[37m' + '')
        return -1

re = 0 # 사용자가 이김 : 1     AI가 이김(사용자가 기권) : -1

while True:
    print('\n시작 단어를 입력해주세요.')
    starting_word = input(('\u001b[33m' + '\n-입력: ')) # 단어 입력 받기
    print('\u001b[37m' + '')

    while True:
        isKor = is_korean(starting_word) # 한국어 여부
        if isKor == 1:
            if len(starting_word) >= 2: # 단어 길이
                check_answer = check(starting_word) # 표준어 탐색기 작동
                if check_answer[0] == 1:
                    re = game(starting_word, word_lst) # 게임 시작
                    break
                else:
                    print('\u001b[31m' + '\n네이버 사전에 없는 단어입니다. 다시 입력해주세요.')
                    print('\u001b[37m' + '')
            else:
                print('\u001b[31m' + '\n2글자 이상의 단어여야 합니다. 다시 입력해주세요.')
                print('\u001b[37m' + '')
        else:
            print('\u001b[31m' + '\n완전한 한국어 단어만 입력 가능합니다. 다시 입력해주세요.')
            print('\u001b[37m' + '')
        starting_word = input(('\u001b[33m' + '\n-입력: '))
        print('\u001b[37m' + '')
    break

if re == -1:
    # AI가 이김(사용자가 기권)
    print("\u001b[\n31m컴퓨터가 이겼습니다!")
else:
    # 사용자가 이김
    print("\u001b[\n96m컴퓨터가 졌습니다!")
print('\u001b[37m' + '')
