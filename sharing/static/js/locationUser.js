ymaps.ready(function () {
    // Геолокация пользователя
    var location = ymaps.geolocation.get();
    // Асинхронная обработка ответа.
    location.then(
        function (result) {
            // Добавление местоположения на карту.
            myMap.geoObjects.add(result.geoObjects)
        },
        function (err) {
            console.log('Ошибка: ' + err)
        }
    );
});