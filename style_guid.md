# Style Guid for writing custom items

_EN: Mayby i translate it later... Try Google translate or somthing similar_

Nazwy przedmiotów dla ścisłości z Vanillą piszemy `sneak_case` czyli każde słowo oddzielone podkreślnikiem
Każdy przedmot ma dwa wymagane obiekty:

 - `id` typu `string` w namespace `minecraft:` Jest to przedmiot który jest wysyłany do gracza, więc musi być z vanilli
 - `nbt` który powinien zawierać 
	- `display` który zawiera `Name` jak JSON z polem `text`
	- `Tags` z listą tagów przedmotu, przynajmniej jeden identyczny z nazwą przedmiotu


```json
{
	"magic_steel": {
		"nbt": {
			"CustomModelData": 6,
			"Enchantments": [],
			"Tags": [
				"Magic Steel"
			],
			"display": {
				"Name": "{\"text\":\"Magic Steel\"}"
			}
		},
		"id": "minecraft:clock"
	}
}
```