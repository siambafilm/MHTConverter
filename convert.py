import os
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.binary_location = '/usr/bin/chromium'

driver = webdriver.Chrome(service=Service(), options=options)

try:
    file_path = os.path.abspath("/home/siamba/Загрузки/Telegram Desktop/eng.mht")
    print("Открываю книгу...")
    driver.get(f"file://{file_path}")
    time.sleep(3)

    # 1. Прокрутка до самого конца для активации скрытых/ленивых страниц (Lazy Loading)
    print("Сканирую и подгружаю страницы книги (имитация прокрутки)...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Крутим вниз большими шагами
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.2)  # Пауза для подгрузки контента
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Если прокрутили до конца экрана, или высота больше не растет — выходим
        current_scroll = driver.execute_script("return window.pageYOffset + window.innerHeight")
        if current_scroll >= last_height or new_height == last_height:
            # Сделаем контрольный рывок на самый верх
            driver.execute_script("window.scrollTo(0, 0);")
            break
        last_height = new_height

    # 2. Мощный скрипт-хак для исправления наслоений страниц
        # 2. Мощный скрипт-хак для исправления наслоений страниц
    print("Выравниваю слои верстки и убираю наслоения...")
    js_fix_layers = """
    // Разворачиваем главные контейнеры
    document.documentElement.style.height = 'auto';
    document.documentElement.style.overflow = 'visible';
    document.body.style.height = 'auto';
    document.body.style.overflow = 'visible';
    
    // Перебираем вообще все элементы на странице
    document.querySelectorAll('*').forEach(el => {
        const style = window.getComputedStyle(el);
        
        // Раскрываем все внутренние скроллбары
        if (style.overflowY === 'scroll' || style.overflowY === 'auto' || el.scrollHeight > el.clientHeight) {
            el.style.height = 'auto';
            el.style.maxHeight = 'none';
            el.style.overflow = 'visible';
        }
        
        // ГЛАВНОЕ: Исправляем наложение. Если элемент зафиксирован или висит в воздухе,
        // возвращаем его в нормальный поток текста, чтобы страницы шли друг за другом.
        if (style.position === 'absolute' || style.position === 'fixed') {
            el.style.position = 'relative';
            el.style.top = 'auto';
            el.style.left = 'auto';
            el.style.transform = 'none';
        }
    });
    """
    driver.execute_script(js_fix_layers)

    time.sleep(3)  # Даем время элементам встать на свои новые места

    # 3. Печать в PDF
    print("Генерирую финальный PDF...")
    print_options = {
        'landscape': False,
        'displayHeaderFooter': False,
        'printBackground': True,
        'preferCSSPageSize': True
    }
    result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
    
    with open("result_book.pdf", "wb") as f:
        f.write(base64.b64decode(result['data']))
        
    print("Успешно! Книга без наложений сохранена в result_book.pdf")

except Exception as e:
    print(f"Ошибка: {e}")

finally:
    driver.quit()

