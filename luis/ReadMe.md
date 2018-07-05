# LUIS: Language Understanding Intelligent Service

The LUIS api allows you to send messages to Azure to be parsed and analyzed for various intents.


## Vocabulary

* **Utterance**: A sentence that a user might use when talking to the bot.  The utterance is parsed for intents and entities.
* **Intent**: What is the action that the user wants to take?  e.g. I want to book a trip or How do I open a service ticket?
* **Entity**: What is the data that "colors" the intent.  If they want to book a trip, where to?  What application do they need service on?
 * Entities are optional but highly recommended.
* **Phrase List**: An open list of related words / phrases.  It is not a set of exact matches.
 * It is used a hint that some words are related.
 * Use phrase lists for rare, proprietary, and foreign words.
 * ([Docs](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-concept-feature))
* **Pattern**: Emphasizes the word order of an utterance to improve intent scoring.
 * It does not help with entity detection and requires entities to be used in the pattern.
 * Patterns increase the confidence score without having to add many utterances.
 * ([Docs](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-concept-patterns))


## Types of Entities

Read the [Official Docs](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-how-plan-your-app#identify-your-entities)

* **Simple Entity**: A single block of text.  e.g. "I'm traveling to *Vienna, Austria*".
* **Hierarchical Entity**: Combines multiple simple entities.
 * Are related to each other in the context of the utterance.
 * Uses specific word choice to indicate each location. Examples of these words include: from/to, leaving/headed to, away from/toward.
 * Both entities are frequently in the same utterance. 
 * Example [tutorial](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-quickstart-intent-and-hier-entity)
* **Composite Entity**: Multiple entities that are pieces to a larger entity.
 * e.g. Ticket Order includes seat count, origin, destination, and date.
 * Example [tutorial](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-tutorial-composite-entity)
* **List Entity**: A list of synonyms.
 * Example [tutorial](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-quickstart-intent-and-list-entity)
* **RegEx Entity**: A regular expression pattern
 * Example [tutorial](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-quickstart-intents-regex-entity)


## Best Practices

Read the [Official Docs](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-concept-best-practices)

* The verb defines the intent.  Book a hotel and book a flight is one intent with two entities.
* Avoid overlapping intents.  
* Don't repeat the same phrase with varying entities.
* Add 10 -15 utterances per re-training to give enough data to make a difference.

## Dispatcher Model

The dispatcher model essentially chains together multiple LUIS calls.  There is a special LUIS application type designed for the dispatch model.

* Read the [Official Docs](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/luis-concept-enterprise#dispatch-tool-and-model)
* Read the [Official Tutorial](https://aka.ms/bot-dispatch)
* Read the [Source Code](https://github.com/Microsoft/botbuilder-tools/tree/master/Dispatch)