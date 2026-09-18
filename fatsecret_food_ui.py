from tkinter import *
from tkinter import messagebox
from fatsecret_food_data import search_food, get_food_detail, save_food_data

# -------------------------------------------------------------------
def search():
    """'검색' 버튼: 식품명으로 검색해서 결과 리스트에 표시"""
    global search_results, current_detail
    keyword = keyword_entry.get().strip()
    if not keyword:
        messagebox.showerror('입력 오류', '식품명을 입력해주세요.')
        return

    try:
        search_results = search_food(keyword)
    except Exception as e:
        messagebox.showerror('검색 실패', str(e))
        return

    current_detail = None
    save_btn.config(state=DISABLED)
    detail_text.delete('1.0', END)

    result_listbox.delete(0, END)
    for item in search_results:
        label = item['name'] if not item['brand'] else f"{item['name']} {item['brand']}"
        result_listbox.insert(END, label)


def view_detail():
    """'영양정보 보기' 버튼: 선택한 항목의 상세 영양정보 조회"""
    global current_detail
    selection = result_listbox.curselection()
    if not selection:
        messagebox.showwarning('선택 필요', '목록에서 식품을 먼저 선택해주세요.')
        return

    food_item = search_results[selection[0]]
    try:
        current_detail = get_food_detail(food_item)
    except Exception as e:
        messagebox.showerror('조회 실패', str(e))
        return

    render(current_detail)
    save_btn.config(state=NORMAL)


def render(detail):
    """조회한 영양정보를 텍스트 위젯에 표시"""
    detail_text.delete('1.0', END)

    title = detail['name'] if not detail['brand'] else f"{detail['name']} {detail['brand']}"

    detail_text.insert(END, '[식품명]\n')
    detail_text.insert(END, f'{title}\n')

    detail_text.insert(END, '\n[영양성분 표]\n')
    for name, value in detail['facts'].items():
        detail_text.insert(END, f'- {name}: {value}\n')

    detail_text.insert(END, '\n[서빙 사이즈별 칼로리]\n')
    for serving in detail['servings']:
        detail_text.insert(END, f"- {serving['serving']}: {serving['calorie']}kcal\n")


def save_data():
    """'저장' 버튼: 현재 조회 결과를 CSV로 저장"""
    if current_detail is None:
        return
    filepath = save_food_data(current_detail)
    messagebox.showinfo('저장 완료', f'{filepath} 에 저장했습니다.')


# - ui ---------------------------------------------------------------

BG = '#f0f8ff'
POINT = '#2b6cb0'
GREEN = '#4caf50'
ORANGE = '#e67e22'

w = Tk()
w.title('fatsecret.kr 영양성분 조회')
w.geometry('480x750')
w.config(bg=BG)

search_results = []
current_detail = None

title_font = ('맑은 고딕', 16, 'bold')
sub_font = ('맑은 고딕', 12)
list_font = ('맑은 고딕', 11)

# ---- 상단: 검색어 입력 ----
top_frame = Frame(w, bg=BG)
top_frame.pack(pady=10)

Label(top_frame, text='식품명:', font=sub_font, bg=BG, fg=POINT).pack(side=LEFT, padx=(0, 5))
keyword_entry = Entry(top_frame, font=sub_font, width=18, bg='white')
keyword_entry.pack(side=LEFT, padx=(0, 5))
Button(top_frame, text='검색', font=sub_font, bg=GREEN, fg='white', command=search).pack(side=LEFT)

# ---- 검색 결과 목록 ----
Label(w, text='검색 결과', font=title_font, bg=BG, fg=POINT).pack(pady=(10, 0))

list_frame = Frame(w, bg=BG)
list_frame.pack(pady=5)

list_scroll = Scrollbar(list_frame)
list_scroll.pack(side=RIGHT, fill=Y)

result_listbox = Listbox(list_frame, font=list_font, width=55, height=8,
                          bg='white', selectbackground=GREEN, selectforeground='white',
                          yscrollcommand=list_scroll.set)
result_listbox.pack(side=LEFT)
list_scroll.config(command=result_listbox.yview)

Button(w, text='영양정보 보기', font=sub_font, bg=POINT, fg='white', command=view_detail).pack(pady=10)

# ---- 상세 영양정보 표시 ----
Label(w, text='영양정보', font=title_font, bg=BG, fg=POINT).pack()

detail_frame = Frame(w, bg=BG)
detail_frame.pack(pady=5)

detail_scroll = Scrollbar(detail_frame)
detail_scroll.pack(side=RIGHT, fill=Y)

detail_text = Text(detail_frame, font=list_font, width=55, height=14,
                    bg='#fffdf5', fg='#333333',
                    yscrollcommand=detail_scroll.set)
detail_text.pack(side=LEFT)
detail_scroll.config(command=detail_text.yview)

# ---- 저장 버튼 ----
save_btn = Button(w, text='저장', font=sub_font, width=12, bg=ORANGE, fg='white',
                   disabledforeground='#999999', command=save_data, state=DISABLED)
save_btn.pack(pady=15)

w.mainloop()
