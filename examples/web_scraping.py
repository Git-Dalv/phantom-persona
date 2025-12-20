"""Пример веб-скрейпинга с phantom-persona.

Демонстрирует использование библиотеки для сбора данных с веб-сайтов
с защитой от детекции ботов.
"""

import asyncio
import json
from datetime import datetime

from phantom_persona import PhantomPersona, ProtectionLevel


async def scrape_quotes():
    """Пример скрейпинга цитат с сайта quotes.toscrape.com.

    Демонстрирует:
    - Навигацию по страницам
    - Извлечение данных
    - Человекоподобное поведение
    - Сохранение результатов
    """
    print("=== Scraping Quotes Example ===")

    quotes_data = []

    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        session = await phantom.new_session()

        try:
            page = await session.new_page()

            # Переходим на сайт с цитатами
            print("Navigating to quotes.toscrape.com...")
            await page.goto("https://quotes.toscrape.com")

            # Собираем цитаты с первых 3 страниц
            for page_num in range(1, 4):
                print(f"Scraping page {page_num}...")

                # Человекоподобная задержка между страницами
                if page_num > 1:
                    await session.human_delay()

                # Извлекаем цитаты
                quotes = await page.query_selector_all(".quote")

                for quote in quotes:
                    # Извлекаем текст цитаты
                    text_elem = await quote.query_selector(".text")
                    text = await text_elem.inner_text() if text_elem else ""

                    # Извлекаем автора
                    author_elem = await quote.query_selector(".author")
                    author = await author_elem.inner_text() if author_elem else ""

                    # Извлекаем теги
                    tag_elems = await quote.query_selector_all(".tag")
                    tags = []
                    for tag_elem in tag_elems:
                        tag = await tag_elem.inner_text()
                        tags.append(tag)

                    # Сохраняем данные
                    quotes_data.append({
                        "text": text,
                        "author": author,
                        "tags": tags,
                        "page": page_num,
                    })

                print(f"✓ Collected {len(quotes)} quotes from page {page_num}")

                # Переход на следующую страницу
                if page_num < 3:
                    next_button = await page.query_selector(".next > a")
                    if next_button:
                        await session.human_click(page, ".next > a")
                        await page.wait_for_load_state("networkidle")

            # Сохраняем результаты
            with open("quotes_data.json", "w", encoding="utf-8") as f:
                json.dump(quotes_data, f, indent=2, ensure_ascii=False)

            print(f"✓ Total quotes collected: {len(quotes_data)}")
            print("✓ Data saved to quotes_data.json")

        finally:
            await session.close()


async def scrape_with_pagination():
    """Пример скрейпинга с пагинацией.

    Демонстрирует обход множества страниц с результатами.
    """
    print("\n=== Pagination Scraping Example ===")

    all_items = []

    async with PhantomPersona(level=ProtectionLevel.MODERATE) as phantom:
        session = await phantom.new_session()

        try:
            page = await session.new_page()

            # Начальная страница
            current_url = "https://quotes.toscrape.com/page/1/"
            await page.goto(current_url)

            page_count = 0

            while True:
                page_count += 1
                print(f"Processing page {page_count}...")

                # Человекоподобное поведение
                await session.human_delay()

                # Прокрутка страницы
                await session.human_scroll(page, distance=300)
                await asyncio.sleep(0.5)

                # Извлекаем данные (пример)
                items = await page.query_selector_all(".quote")
                all_items.extend(items)

                print(f"✓ Found {len(items)} items on page {page_count}")

                # Проверяем наличие кнопки "Next"
                next_button = await page.query_selector(".next > a")

                if not next_button:
                    print("✓ No more pages")
                    break

                if page_count >= 3:  # Ограничение для примера
                    print("✓ Reached page limit for example")
                    break

                # Переход на следующую страницу
                await next_button.click()
                await page.wait_for_load_state("networkidle")

            print(f"✓ Total items collected: {len(all_items)}")

        finally:
            await session.close()


async def scrape_dynamic_content():
    """Пример скрейпинга динамического контента.

    Демонстрирует работу с JavaScript-загружаемым контентом.
    """
    print("\n=== Dynamic Content Scraping Example ===")

    async with PhantomPersona(level=ProtectionLevel.ADVANCED) as phantom:
        session = await phantom.new_session()

        try:
            page = await session.new_page()

            # Переходим на страницу с JavaScript
            print("Loading page with JavaScript content...")
            await page.goto("https://quotes.toscrape.com/js/")

            # Ждём загрузки динамического контента
            print("Waiting for dynamic content...")
            await page.wait_for_selector(".quote", timeout=10000)

            # Дополнительная задержка для полной загрузки
            await asyncio.sleep(2)

            # Прокрутка для загрузки lazy-loaded контента
            await session.human_scroll(page, distance=500)
            await asyncio.sleep(1)

            # Извлекаем данные
            quotes = await page.query_selector_all(".quote")
            print(f"✓ Found {len(quotes)} quotes (loaded via JavaScript)")

            # Получаем данные первой цитаты
            if quotes:
                first_quote = quotes[0]
                text = await first_quote.query_selector(".text")
                if text:
                    quote_text = await text.inner_text()
                    print(f"✓ First quote: {quote_text[:50]}...")

        finally:
            await session.close()


async def scrape_with_login():
    """Пример скрейпинга с авторизацией.

    Демонстрирует вход на сайт и работу с защищёнными страницами.

    Note:
        Этот пример использует демо-сайт с тестовыми креденшелами.
    """
    print("\n=== Login Scraping Example ===")

    async with PhantomPersona(level=ProtectionLevel.ADVANCED) as phantom:
        session = await phantom.new_session()

        try:
            page = await session.new_page()

            # Переходим на страницу логина
            print("Navigating to login page...")
            await page.goto("https://quotes.toscrape.com/login")

            # Человекоподобное заполнение формы
            print("Filling login form...")
            await session.human_delay()

            # Вводим username
            await session.human_type(page, "#username", "admin")
            await session.human_delay()

            # Вводим password
            await session.human_type(page, "#password", "admin")
            await session.human_delay()

            # Нажимаем кнопку логина
            print("Submitting login form...")
            await session.human_click(page, 'input[type="submit"]')

            # Ждём редиректа
            await page.wait_for_load_state("networkidle")

            # Проверяем успешность логина
            current_url = page.url
            if "/login" not in current_url:
                print("✓ Login successful!")

                # Теперь можем скрейпить защищённый контент
                # (в этом примере просто проверяем, что залогинены)
                logout_link = await page.query_selector("a[href='/logout']")
                if logout_link:
                    print("✓ Confirmed: user is logged in")
            else:
                print("✗ Login failed")

        finally:
            await session.close()


async def scrape_with_error_handling():
    """Пример скрейпинга с обработкой ошибок.

    Демонстрирует устойчивый к ошибкам скрейпинг.
    """
    print("\n=== Error Handling Scraping Example ===")

    successful_pages = 0
    failed_pages = 0

    urls = [
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/",
        "https://this-page-does-not-exist/",  # Ошибка
        "https://quotes.toscrape.com/page/3/",
    ]

    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        session = await phantom.new_session()

        try:
            for url in urls:
                try:
                    print(f"Attempting to scrape: {url}")
                    page = await session.new_page()

                    # Пробуем загрузить страницу с таймаутом
                    await page.goto(url, timeout=5000)

                    # Если успешно, извлекаем данные
                    quotes = await page.query_selector_all(".quote")
                    print(f"✓ Success: found {len(quotes)} quotes")
                    successful_pages += 1

                    await page.close()

                except Exception as e:
                    print(f"✗ Error scraping {url}: {type(e).__name__}")
                    failed_pages += 1
                    continue

                # Человекоподобная задержка между страницами
                await session.human_delay()

            print(f"\n✓ Successful pages: {successful_pages}")
            print(f"✗ Failed pages: {failed_pages}")

        finally:
            await session.close()


async def scrape_and_save():
    """Пример скрейпинга с сохранением в разных форматах.

    Демонстрирует сохранение данных в JSON, CSV, и скриншоты.
    """
    print("\n=== Scrape and Save Example ===")

    import csv

    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        session = await phantom.new_session()

        try:
            page = await session.new_page()
            await page.goto("https://quotes.toscrape.com")

            # Извлекаем данные
            quotes_data = []
            quotes = await page.query_selector_all(".quote")

            for quote in quotes:
                text_elem = await quote.query_selector(".text")
                author_elem = await quote.query_selector(".author")

                text = await text_elem.inner_text() if text_elem else ""
                author = await author_elem.inner_text() if author_elem else ""

                quotes_data.append({
                    "text": text.strip('"'),
                    "author": author,
                    "timestamp": datetime.now().isoformat(),
                })

            # Сохраняем в JSON
            with open("quotes.json", "w", encoding="utf-8") as f:
                json.dump(quotes_data, f, indent=2, ensure_ascii=False)
            print("✓ Saved to quotes.json")

            # Сохраняем в CSV
            with open("quotes.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["text", "author", "timestamp"])
                writer.writeheader()
                writer.writerows(quotes_data)
            print("✓ Saved to quotes.csv")

            # Сохраняем скриншот страницы
            await page.screenshot(path="quotes_page.png", full_page=True)
            print("✓ Saved screenshot to quotes_page.png")

            # Сохраняем HTML
            html_content = await page.content()
            with open("quotes_page.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("✓ Saved HTML to quotes_page.html")

            print(f"\n✓ Total quotes saved: {len(quotes_data)}")

        finally:
            await session.close()


async def main():
    """Запуск всех примеров скрейпинга."""
    print("=" * 60)
    print("Phantom Persona - Web Scraping Examples")
    print("=" * 60)

    await scrape_quotes()
    await scrape_with_pagination()
    await scrape_dynamic_content()
    await scrape_with_login()
    await scrape_with_error_handling()
    await scrape_and_save()

    print("\n" + "=" * 60)
    print("All scraping examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
