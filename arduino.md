# Jak přečíst arduino kód

## AVRDude

Pro přečtení kódu z arduina je potřeba použít AVRDude (implementovaný v Arduino IDE)

Tento příkaz se normálně spouští při uploadu kompilovaného kódu do Arduina UNO

```bash
"C:\cesta\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino17/bin/avrdude" "-CC:\cesta\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino17/etc/avrdude.conf" -v -V -patmega328p -carduino "-PCOM4" -b115200 -D "-Uflash:w:C:\cesta/filename.ino.hex:i"
```



* **Uprav příkaz AVRDUDE** pro čtení binárního kódu:
  * Zkopíruj příkaz z konzolového okna.
  * Vlož ho do textového editoru a uprav ho tak, aby četl binární kód místo zápisu. Změň část příkazu `-Uflash:w:C:\cesta/filename.hex:i` na `-Uflash:r:C:\cesta/filename.hex:i`.
* **Spusť upravený příkaz** :
  * Připoj Arduino zpět k počítači.
  * Otevři příkazový řádek (CMD) a vlož upravený příkaz.
  * Spusť příkaz pro čtení binárního kódu z Arduino.

> Pozn.: Jak zjistit cestu je zcela jednoduché:
>
> * **Připoj Arduino Uno k počítači** pomocí USB kabelu. (Pro načtení COM portu - nezapomeň že desku musíš připojovat do stejného usb, nebo budeš muset přepisovat COM port)
> * **Otevři Arduino IDE** a vyber svůj board a port z nabídky **Nástroje > Deska** a  **Nástroje > Port** .
> * **Vygeneruj příkaz AVRDUDE** :
>
>   * Odpoj Arduino od počítače.
>   * V Arduino IDE jdi do **Soubor > Vlastnosti** a zaškrtni políčko vedle  **Zobrazit podrobné výstupy během > nahrávání** .
>   * Zkus nahrát nějaký sketch přes **Sketch > Nahrát** (tento krok selže, protože deska není připojena).
>   * V konzolovém okně vyhledej vygenerovaný příkaz AVRDUDE.

## AVRDisassembler

> https://github.com/twinearthsoftware/AVRDisassembler?tab=readme-ov-file

Tento program přeloží hex soubor (získaný pomocí AVRDude) na asm

## Další zajímevé programy

https://github.com/NationalSecurityAgency/ghidra

https://simulide.com/p/download110/
