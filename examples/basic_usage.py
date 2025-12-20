"""Basic usage examples for phantom-persona.

This file demonstrates the core capabilities of the phantom-persona library
for browser automation with bot detection protection.
"""

import asyncio

from phantom_persona import PhantomPersona, ProtectionLevel


async def basic_example():
    """Basic usage with context manager.

    Creates a PhantomPersona client with basic protection level,
    opens a page and takes a screenshot.
    """
    print("=== Basic Example ===")

    # Use async context manager for automatic cleanup
    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        # Create session
        session = await phantom.new_session()

        # Create page
        page = await session.new_page()

        # Navigate to bot detection site
        print("Navigating to bot detection site...")
        await page.goto("https://bot.sannysoft.com", wait_until="networkidle")

        # Give page time to run tests
        await asyncio.sleep(3)

        # Save screenshot
        await page.screenshot(path="detection_test.png")
        print("✓ Screenshot saved to detection_test.png")

        # Get page title
        title = await page.title()
        print(f"✓ Page title: {title}")

        # Close session
        await session.close()

    print("✓ Browser closed automatically")


async def session_example():
    """Example of working with sessions.

    Demonstrates session creation and usage,
    as well as human-like behavior.
    """
    print("\n=== Session Example ===")

    # Create client with MODERATE protection level
    async with PhantomPersona(level=ProtectionLevel.MODERATE) as phantom:
        # Create session
        session = await phantom.new_session()

        try:
            # Create page
            page = await session.new_page()

            # Navigate to site
            print("Navigating to example.com...")
            await page.goto("https://example.com")

            # Human-like delay before actions
            print("Simulating human delay...")
            await session.human_delay()

            # Get information from page
            title = await page.title()
            url = page.url
            print(f"✓ Title: {title}")
            print(f"✓ URL: {url}")

            # Scroll page (human-like)
            print("Scrolling page...")
            await session.human_scroll(page, distance=500)

        finally:
            # Always close session
            await session.close()

    print("✓ Session closed")


async def multiple_pages_example():
    """Пример работы с несколькими страницами.

    Демонстрирует открытие нескольких страниц в одной сессии.
    """
    print("\n=== Multiple Pages Example ===")

    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        session = await phantom.new_session()

        try:
            # Открываем первую страницу
            page1 = await session.new_page()
            await page1.goto("https://example.com")
            title1 = await page1.title()
            print(f"✓ Page 1: {title1}")

            # Открываем вторую страницу
            page2 = await session.new_page()
            await page2.goto("https://www.wikipedia.org")
            title2 = await page2.title()
            print(f"✓ Page 2: {title2}")

            # Обе страницы используют одну и ту же сессию/персону
            print(f"✓ Both pages share the same session")

        finally:
            await session.close()


async def human_behavior_example():
    """Пример человекоподобного поведения.

    Демонстрирует методы для имитации человеческого поведения:
    - human_delay() - случайные задержки
    - human_type() - медленный ввод текста
    - human_click() - клик с задержкой
    - human_scroll() - плавная прокрутка
    """
    print("\n=== Human Behavior Example ===")

    async with PhantomPersona(level=ProtectionLevel.ADVANCED) as phantom:
        session = await phantom.new_session()

        try:
            page = await session.new_page()

            # Переходим на страницу с формой поиска
            print("Navigating to search page...")
            await page.goto("https://www.google.com")

            # Человеческая задержка
            await session.human_delay()

            # Находим поле поиска
            search_input = await page.query_selector('textarea[name="q"]')
            if search_input:
                # Вводим текст по-человечески (медленно)
                print("Typing search query...")
                await session.human_type(
                    page,
                    'textarea[name="q"]',
                    "phantom persona library"
                )

                # Задержка перед отправкой
                await session.human_delay()

                # Можем нажать Enter или кликнуть на кнопку
                await page.keyboard.press("Enter")

                print("✓ Search submitted")

                # Ждём результатов
                await page.wait_for_timeout(2000)

        finally:
            await session.close()


async def custom_persona_example():
    """Пример создания кастомной персоны.

    Демонстрирует создание персоны с кастомными параметрами:
    - Географическое местоположение
    - Устройство и fingerprint
    - User agent
    """
    print("\n=== Custom Persona Example ===")

    from phantom_persona import DeviceInfo, Fingerprint, GeoInfo, Persona
    from datetime import datetime

    # Создаём географическую информацию
    geo = GeoInfo(
        country_code="DE",
        country="Germany",
        city="Berlin",
        timezone="Europe/Berlin",
        language="de-DE",
        languages=["de-DE", "de", "en-US", "en"],
    )

    # Создаём информацию об устройстве
    device = DeviceInfo(
        type="desktop",
        platform="Win32",
        vendor="Google Inc.",
        renderer="ANGLE (Intel, Mesa Intel(R) UHD Graphics 620)",
        screen_width=1920,
        screen_height=1080,
        color_depth=24,
        pixel_ratio=1.0,
    )

    # Создаём fingerprint
    fingerprint = Fingerprint(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        device=device,
        canvas_hash="de_canvas_123",
        webgl_hash="de_webgl_456",
        fonts=["Arial", "Times New Roman", "Segoe UI"],
    )

    # Создаём персону
    persona = Persona(
        fingerprint=fingerprint,
        geo=geo,
        created_at=datetime.now(),
    )

    print(f"✓ Created persona with ID: {persona.id}")
    print(f"✓ Location: {geo.city}, {geo.country}")
    print(f"✓ Language: {geo.language}")

    # Используем кастомную персону
    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        session = await phantom.new_session(persona=persona)

        try:
            page = await session.new_page()
            await page.goto("https://browserleaks.com/javascript")

            # Проверяем, что настройки применились
            page_lang = await page.evaluate("navigator.language")
            page_ua = await page.evaluate("navigator.userAgent")

            print(f"✓ Page language: {page_lang}")
            print(f"✓ User agent contains: ...{page_ua[-50:]}")

        finally:
            await session.close()


async def proxy_example():
    """Пример использования прокси.

    Демонстрирует подключение через прокси-сервер.

    Note:
        Замените proxy_url на реальный прокси для тестирования.
    """
    print("\n=== Proxy Example ===")

    from phantom_persona.proxy import ProxyInfo

    # Создаём прокси из URL
    # proxy = ProxyInfo.from_url("http://user:pass@proxy.example.com:8080")

    # Или из строки
    # proxy = ProxyInfo.from_string("proxy.example.com:8080:user:pass")

    # Пример с публичным прокси (не рекомендуется для продакшена)
    print("⚠ Proxy example disabled - configure your proxy first")
    print("Uncomment proxy configuration in the code to test")

    # async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
    #     session = await phantom.new_session(proxy=proxy)
    #
    #     try:
    #         page = await session.new_page()
    #         await page.goto("https://api.ipify.org?format=json")
    #
    #         # Получаем IP
    #         content = await page.content()
    #         print(f"✓ IP response: {content}")
    #
    #     finally:
    #         await session.close()


async def config_file_example():
    """Пример загрузки конфигурации из файла.

    Демонстрирует использование YAML/JSON конфигурации.
    """
    print("\n=== Config File Example ===")

    from phantom_persona.config import ConfigLoader

    # Создаём конфигурацию из уровня защиты
    config = ConfigLoader.from_level(level=3)  # ADVANCED

    print(f"✓ Config created with level: {config.level}")
    print(f"✓ Browser type: {config.browser.type}")
    print(f"✓ Headless: {config.browser.headless}")

    # Можно также загрузить из файла:
    # config = ConfigLoader.load("config.yaml")

    # Используем конфигурацию
    async with PhantomPersona(config=config) as phantom:
        print(f"✓ Loaded {len(phantom.plugins)} plugins for protection level {config.level}")


async def convenience_method_example():
    """Пример использования convenience методов.

    Демонстрирует упрощённые методы для быстрого старта.
    """
    print("\n=== Convenience Method Example ===")

    # Метод new_page() создаёт и сессию, и страницу автоматически
    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        # Быстрое создание страницы (без явного создания сессии)
        page = await phantom.new_page()

        await page.goto("https://example.com")
        title = await page.title()

        print(f"✓ Quick page created")
        print(f"✓ Title: {title}")

        # Примечание: при использовании new_page() вы не получаете
        # прямой доступ к сессии, поэтому не можете использовать
        # методы human_* напрямую. Для этого используйте new_session().


async def error_handling_example():
    """Пример обработки ошибок.

    Демонстрирует правильную обработку ошибок при работе с библиотекой.
    """
    print("\n=== Error Handling Example ===")

    from phantom_persona.core.exceptions import (
        BrowserException,
        BrowserLaunchError,
        PhantomException,
    )

    try:
        async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
            session = await phantom.new_session()

            try:
                page = await session.new_page()

                # Попытка перейти на несуществующий сайт
                await page.goto("https://this-site-does-not-exist-12345.com", timeout=5000)

            except Exception as e:
                print(f"⚠ Navigation error (expected): {type(e).__name__}")

            finally:
                await session.close()

    except BrowserLaunchError as e:
        print(f"✗ Failed to launch browser: {e.message}")
    except BrowserException as e:
        print(f"✗ Browser error: {e.message}")
    except PhantomException as e:
        print(f"✗ Phantom error: {e.message}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    print("✓ Error handling completed")


async def main():
    """Запуск всех примеров."""
    print("=" * 60)
    print("Phantom Persona - Basic Usage Examples")
    print("=" * 60)

    # Запускаем примеры по очереди
    await basic_example()
    await session_example()
    await multiple_pages_example()
    await human_behavior_example()
    await custom_persona_example()
    await proxy_example()
    await config_file_example()
    await convenience_method_example()
    await error_handling_example()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Запуск всех примеров
    asyncio.run(main())
