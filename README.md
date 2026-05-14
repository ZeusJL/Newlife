# Новая Жизнь APK

Это готовый Kivy-проект для сборки полноценного Android APK.

## Что внутри

- `main.py` — игра.
- `buildozer.spec` — настройки Android-сборки.
- `.github/workflows/build-apk.yml` — автоматическая сборка APK через GitHub Actions.

## Как собрать APK через GitHub на телефоне

1. Создай новый репозиторий на GitHub.
2. Загрузи все файлы из этой папки в репозиторий.
3. Открой вкладку `Actions`.
4. Запусти workflow `Build Android APK`.
5. Дождись окончания сборки.
6. Открой завершённую сборку и скачай artifact `NewLife-debug-apk`.
7. Внутри будет APK, который можно установить на Android.

## Важно

Первый билд может идти долго: GitHub будет скачивать Android SDK/NDK и зависимости.
APK будет debug-версией. Для публикации в Google Play нужен release-билд и подпись.
