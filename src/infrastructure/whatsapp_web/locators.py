from selenium.webdriver.common.by import By


SESSION_ACTIVE_LOCATORS = [
    (By.CSS_SELECTOR, "#pane-side"),
    (By.XPATH, "//input[@data-tab='3' and @role='textbox']"),
    (By.XPATH, "//input[contains(@aria-label, 'Buscar un chat')]"),
    (By.XPATH, "//button[@aria-label='Nuevo chat']"),
    (By.XPATH, "//button[@aria-label='Menú']"),
    (By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"),
]

OPEN_CHAT_LOCATORS = [
    (By.CSS_SELECTOR, "#main"),
    (By.CSS_SELECTOR, "#main header"),
    (By.CSS_SELECTOR, "#main footer"),
    (By.XPATH, "//div[@role='textbox' and contains(@aria-label, 'Escribir un mensaje')]"),
    (By.XPATH, "//button[@aria-label='Enviar' or @aria-label='Send']"),
]

MESSAGE_COMPOSER_LOCATORS = [
    (By.XPATH, "//div[@role='textbox' and contains(@aria-label, 'Escribir un mensaje')]"),
    (By.XPATH, "//footer//*[@role='textbox' and @contenteditable='true']"),
    (By.CSS_SELECTOR, "footer [contenteditable='true'][role='textbox']"),
    (By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"),
]

SEND_BUTTON_LOCATORS = [
    (By.XPATH, "//button[@aria-label='Enviar' or @aria-label='Send']"),
]
