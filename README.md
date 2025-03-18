# Opis projektu

Projekt polega na stworzeniu autonomicznej platformy mobilnej, zdolnej do omijania przeszkód oraz przemieszczania się na określoną odległość w zadanym kierunku. Robot wykorzystuje technologię LIDAR do detekcji przeszkód i analizowania otoczenia.

## Główne komponenty

Raspberry Pi – jednostka sterująca, odpowiedzialna za przetwarzanie danych i zarządzanie ruchem.</br>

Arduino – pośrednik między Raspberry Pi a silnikami krokowymi.</br>

Silniki krokowe – napęd robota, sterowane poprzez Arduino.</br>

LIDAR – system skanujący otoczenie w celu wykrywania przeszkód.</br>

Zasilanie – odpowiednie moduły zasilające dla Raspberry Pi, Arduino oraz silników.</br>

## Oprogramowanie

Python – główny język programowania używany do przetwarzania danych z LIDAR-a i sterowania ruchem robota.</br>

Arduino (C++) – oprogramowanie odpowiedzialne za sterowanie silnikami krokowymi.</br>

## Funkcjonalność

Analiza otoczenia – LIDAR zbiera dane o przeszkodach i przekazuje je do Raspberry Pi.</br>

Przetwarzanie danych – skrypty w Pythonie analizują dane i podejmują decyzję o trasie.</br>

Sterowanie ruchem – Raspberry Pi wysyła komendy do Arduino, które steruje silnikami krokowymi.</br>

Omijanie przeszkód – robot wykrywa przeszkody i koryguje trasę, aby ich uniknąć.</br>

Przemieszczanie na określoną odległość – możliwość zaprogramowania trasy na podstawie zadanych parametrów.</br>
