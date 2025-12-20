# Phantom Persona - Examples

Примеры использования библиотеки phantom-persona для автоматизации браузера с защитой от детекции.

## Список примеров

### 1. basic_usage.py

Базовые примеры использования библиотеки:

- **basic_example()** - Простейший пример с context manager
- **session_example()** - Работа с сессиями
- **multiple_pages_example()** - Несколько страниц в одной сессии
- **human_behavior_example()** - Человекоподобное поведение
- **custom_persona_example()** - Создание кастомной персоны
- **proxy_example()** - Использование прокси
- **config_file_example()** - Загрузка конфигурации
- **convenience_method_example()** - Упрощённые методы
- **error_handling_example()** - Обработка ошибок

### Запуск примеров

Запустить все примеры:

```bash
python examples/basic_usage.py
```

Запустить отдельную функцию (отредактируйте main()):

```python
if __name__ == "__main__":
    asyncio.run(basic_example())
```

## Требования

Перед запуском примеров установите:

```bash
# Установить библиотеку
pip install -e .

# Установить браузеры Playwright
playwright install chromium firefox webkit
```

## Основные концепции

### PhantomPersona Client

Главная точка входа в библиотеку:

```python
from phantom_persona import PhantomPersona, ProtectionLevel

# Создание с уровнем защиты
async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
    # Используем phantom для создания сессий
    pass
```

### Уровни защиты

- **NONE (0)** - Без защиты от детекции
- **BASIC (1)** - Базовая защита (webdriver hiding)
- **MODERATE (2)** - Средняя защита
- **ADVANCED (3)** - Продвинутая защита
- **STEALTH (4)** - Максимальная защита

### Сессии

Сессия представляет одну браузерную сессию с персоной:

```python
session = await phantom.new_session()
page = await session.new_page()

# Человекоподобные действия
await session.human_delay()
await session.human_type(page, "#input", "text")
await session.human_click(page, "#button")

await session.close()
```

### Персоны

Персона - это уникальная идентичность браузера:

```python
from phantom_persona import Persona, GeoInfo, DeviceInfo, Fingerprint

# Создание кастомной персоны
persona = Persona(
    fingerprint=fingerprint,
    geo=geo,
    created_at=datetime.now(),
)

# Использование персоны
session = await phantom.new_session(persona=persona)
```

### Прокси

Подключение через прокси:

```python
from phantom_persona.proxy import ProxyInfo

# Из URL
proxy = ProxyInfo.from_url("http://user:pass@proxy.com:8080")

# Из строки
proxy = ProxyInfo.from_string("proxy.com:8080:user:pass")

# Использование
session = await phantom.new_session(proxy=proxy)
```

## Примеры использования

### Быстрый старт

```python
import asyncio
from phantom_persona import PhantomPersona, ProtectionLevel

async def quick_start():
    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        session = await phantom.new_session()
        page = await session.new_page()

        await page.goto("https://example.com")
        title = await page.title()
        print(f"Title: {title}")

        await session.close()

asyncio.run(quick_start())
```

### Проверка детекции

```python
async def check_detection():
    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        session = await phantom.new_session()
        page = await session.new_page()

        await page.goto("https://bot.sannysoft.com")
        await page.screenshot(path="detection_result.png")

        await session.close()
```

### Форма с человеческим поведением

```python
async def fill_form():
    async with PhantomPersona(level=ProtectionLevel.ADVANCED) as phantom:
        session = await phantom.new_session()
        page = await session.new_page()

        await page.goto("https://example.com/form")

        # Человекоподобный ввод
        await session.human_type(page, "#name", "John Doe")
        await session.human_delay()

        await session.human_type(page, "#email", "john@example.com")
        await session.human_delay()

        await session.human_click(page, "#submit")

        await session.close()
```

### Множественные страницы

```python
async def multiple_tabs():
    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        session = await phantom.new_session()

        # Первая страница
        page1 = await session.new_page()
        await page1.goto("https://example.com")

        # Вторая страница (в той же сессии)
        page2 = await session.new_page()
        await page2.goto("https://google.com")

        # Обе страницы используют одну персону

        await session.close()
```

## Best Practices

### 1. Всегда используйте context manager

```python
# ✓ Хорошо
async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
    # код

# ✗ Плохо (нужно вручную вызывать close)
phantom = PhantomPersona(level=ProtectionLevel.BASIC)
await phantom.start()
# ... код ...
await phantom.close()
```

### 2. Закрывайте сессии

```python
session = await phantom.new_session()
try:
    # работа с сессией
    pass
finally:
    await session.close()
```

### 3. Используйте человекоподобное поведение

```python
# ✓ Хорошо - имитация человека
await session.human_delay()
await session.human_type(page, "#input", "text")
await session.human_click(page, "#button")

# ✗ Плохо - слишком быстро
await page.fill("#input", "text")
await page.click("#button")
```

### 4. Обрабатывайте ошибки

```python
from phantom_persona.core.exceptions import PhantomException

try:
    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        # код
        pass
except PhantomException as e:
    print(f"Error: {e.message}")
    print(f"Details: {e.details}")
```

### 5. Используйте разные уровни защиты

```python
# Для простых задач
PhantomPersona(level=ProtectionLevel.BASIC)

# Для строгих сайтов
PhantomPersona(level=ProtectionLevel.ADVANCED)

# Для максимальной скрытности
PhantomPersona(level=ProtectionLevel.STEALTH)
```

## Troubleshooting

### Браузер не запускается

```bash
# Установите браузеры Playwright
playwright install chromium
```

### Детекция всё равно происходит

```python
# Попробуйте увеличить уровень защиты
async with PhantomPersona(level=ProtectionLevel.STEALTH) as phantom:
    # ...
```

### Медленная работа

```python
# Используйте headless режим
from phantom_persona.config import BrowserConfig

config = BrowserConfig(headless=True)
async with PhantomPersona(config=config) as phantom:
    # ...
```

## Дополнительные ресурсы

- [Документация Playwright](https://playwright.dev/python/)
- [API Reference](../README.md)
- [Тесты](../tests/) - больше примеров использования

## Вопросы?

Если у вас возникли вопросы или проблемы, создайте issue в репозитории проекта.
