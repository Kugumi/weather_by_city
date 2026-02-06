import requests

def handler(vars: dict, params: dict) -> dict:

    city = params.get('city', '').strip()
    api_key = vars.get('api_key', '').strip()

    if not city:
        return {
            'success': False,
            'error': 'Не указан город. Используйте параметр "city"',
            'data': None
        }
    if not api_key:
        return {
            'success': False,
            'error': 'Не указан ключ API. Укажите его в vars["api_key"]',
            'data': None
        }

    DEFAULT_CONFIG = {
        'api_key': api_key,
        'base_url': 'http://api.openweathermap.org/data/2.5/weather',
        'units': 'metric',  # metric для °C
        'lang': 'ru'
    }

    request_params = {
        'q': city,
        'appid': DEFAULT_CONFIG['api_key'],
        'units': DEFAULT_CONFIG['units'],
        'lang': 'ru'
    }

    try:
        response = requests.get(
            DEFAULT_CONFIG['base_url'],
            params=request_params,
            timeout=10
        )

        response.raise_for_status()
        weather_data = response.json()

        if 'cod' in weather_data and weather_data['cod'] != 200:
            error_message = weather_data.get('message', 'Неизвестная ошибка API')
            return {
                'success': False,
                'error': f'Ошибка API: {error_message}',
                'data': None
            }

        # Извлечение ключевых данных
        extracted_data = {
            'city': weather_data.get('name', ''), # город
            'temperature': weather_data.get('main', {}).get('temp'), # температура
            'feels_like': weather_data.get('main', {}).get('feels_like'), # ощущается как
            'humidity': weather_data.get('main', {}).get('humidity'),  # влажность
            'weather_description': weather_data.get('weather', [{}])[0].get('description', ''), # пасмурно, солнечно и т.д.
            'wind_speed': weather_data.get('wind', {}).get('speed'),  # скорость ветра м/с
            'cloudiness': weather_data.get('clouds', {}).get('all'),  # облачность %
        }

        if extracted_data['temperature'] is not None:
            extracted_data['temperature_with_unit'] = f"{extracted_data['temperature']}°C"

        return {
            'success': True,
            'error': None,
            'data': extracted_data,
            'source': 'OpenWeatherMap',
            'units': {
                'temperature': '°C',
                'pressure': 'hPa',
                'wind_speed': 'м/с',
                'visibility': 'метры'
            }
        }

    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Таймаут при подключении к сервису погоды',
            'data': None
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': 'Ошибка подключения к сервису погоды',
            'data': None
        }
    except requests.exceptions.HTTPError as e:
        return {
            'success': False,
            'error': f'HTTP ошибка: {str(e)}',
            'data': None
        }
    except ValueError as e:
        return {
            'success': False,
            'error': f'Ошибка парсинга JSON: {str(e)}',
            'data': None
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Неизвестная ошибка: {str(e)}',
            'data': None
        }

if __name__ == "__main__":
    # Пример 1: Успешный запрос
    result = handler(
        vars={'api_key': '376d35a0660e2980d34846f7d2b15a05'},
        params={'city': 'Москва'}
    )
    print(f"Успешно: {result.get('success')}")
    if result.get('success'):
        data = result.get('data', {})
        print(f"Город: {data.get('city')}")
        print(f"Температура: {data.get('temperature_with_unit')}")
        print(f"Ощущается как: {data.get('feels_like')}°C")
        print(f"Погода: {data.get('weather_description')}")
        print(f"Влажность: {data.get('humidity')}%")
        print(f"Ветер: {data.get('wind_speed')} м/с")
    else:
        print(f"Ошибка: {result.get('error')}")

    print("\nГород не указан")
    result = handler(vars={}, params={})
    print(f"Успешно: {result.get('success')}")
    print(f"Ошибка: {result.get('error')}")

    print("\nНеверный API ключ")
    result = handler(
        vars={'api_key': 'неверный_ключ'},
        params={'city': 'Москва'}
    )
    print(f"Успешно: {result.get('success')}")
    print(f"Ошибка: {result.get('error')}")