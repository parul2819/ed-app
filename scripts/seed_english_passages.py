"""Seed hand-written English reading-comprehension passages.

One passage per difficulty_rank, 1 through 50 -- the full ladder defined in
reading_levels.py -- each run through validate_passage() before anything is
written to the database -- exactly the checks a real content pipeline would
need to pass.

Usage:
    poetry run python scripts/seed_english_passages.py                 # validate, then insert
    poetry run python scripts/seed_english_passages.py --validate-only  # validate only, no DB writes
"""

import argparse
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from learn_with_masti.db import SessionLocal  # noqa: E402
from learn_with_masti.models import ComprehensionQuestion, Passage  # noqa: E402
from learn_with_masti.schemas import ComprehensionQuestion as ComprehensionQuestionSchema  # noqa: E402
from learn_with_masti.schemas import PassageDetail  # noqa: E402
from learn_with_masti.validation import _sentence_count, validate_passage  # noqa: E402


@dataclass
class QuestionSeed:
    question_type: str
    question_text: str
    options: list[str]
    correct_answer: str
    explanation_hint: str


@dataclass
class PassageSeed:
    title: str
    body: str
    difficulty_rank: int
    takeaway: str
    questions: list[QuestionSeed]


PASSAGES: list[PassageSeed] = [
    PassageSeed(
        title="The Mango Tree",
        body=(
            "Ravi has a mango tree. It grows near his small house. "
            "The tree is old and tall. Green leaves cover the whole tree. "
            "Fruit grows on it each May. At first the fruit is green. "
            "Soon the mango turns bright yellow. Ravi picks one and eats it."
        ),
        difficulty_rank=1,
        takeaway="Fruit changes color as it ripens.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What does Ravi have?",
                ["Mango tree", "Red car", "Small dog", "Big house"],
                "Mango tree",
                "The passage says Ravi has a mango tree.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where does the tree grow?",
                ["House", "Park", "River", "School"],
                "House",
                "The passage says the tree grows near his house.",
            ),
            QuestionSeed(
                "literal_recall",
                "What color does mango turn?",
                ["Yellow", "Blue", "Purple", "Black"],
                "Yellow",
                "The passage says the mango turns bright yellow.",
            ),
            QuestionSeed(
                "literal_recall",
                "How is the tree?",
                ["Old and tall", "Short and new", "Thin and small", "New and short"],
                "Old and tall",
                "The passage says the tree is old and tall.",
            ),
            QuestionSeed(
                "literal_recall",
                "What covers the tree?",
                ["Green leaves", "Red flowers", "White snow", "Small stones"],
                "Green leaves",
                "The passage says green leaves cover the tree.",
            ),
            QuestionSeed(
                "literal_recall",
                "When does the fruit grow?",
                ["May", "July", "January", "October"],
                "May",
                "The passage says fruit grows on it each May.",
            ),
            QuestionSeed(
                "literal_recall",
                "What does Ravi do with it?",
                ["Eats it", "Throws it", "Paints it", "Hides it"],
                "Eats it",
                "The passage says Ravi picks one and eats it.",
            ),
        ],
    ),
    PassageSeed(
        title="A Rainy Day",
        body=(
            "Meena looks out the window. Dark clouds fill the sky. "
            "Soon the rain begins to fall. Meena wears her yellow coat. "
            "She jumps in a puddle. Her socks get very wet. "
            "Meena laughs and jumps more. The rain stops after a while. "
            "Colors fill the whole sky. Meena runs inside for cocoa."
        ),
        difficulty_rank=2,
        takeaway="Rainy days can still be fun if you dress for them.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What does Meena look out of?",
                ["Window", "Door", "Wall", "Roof"],
                "Window",
                "The passage says Meena looks out the window.",
            ),
            QuestionSeed(
                "literal_recall",
                "What fills the sky first?",
                ["Dark clouds", "Bright sun", "White snow", "Green grass"],
                "Dark clouds",
                "The passage says dark clouds fill the sky.",
            ),
            QuestionSeed(
                "literal_recall",
                "What color is Meena's coat?",
                ["Yellow", "Red", "Blue", "Green"],
                "Yellow",
                "The passage says Meena wears her yellow coat.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where does Meena jump?",
                ["A puddle", "A wall", "A tree", "A bed"],
                "A puddle",
                "The passage says she jumps in a puddle.",
            ),
            QuestionSeed(
                "literal_recall",
                "How do her socks get?",
                ["Very wet", "Very dry", "Very hot", "Very cold"],
                "Very wet",
                "The passage says her socks get very wet.",
            ),
            QuestionSeed(
                "literal_recall",
                "What does Meena do after jumping?",
                ["Laughs more", "Cries loudly", "Sits quietly", "Sleeps deeply"],
                "Laughs more",
                "The passage says Meena laughs and jumps more.",
            ),
            QuestionSeed(
                "literal_recall",
                "What fills the sky after the rain?",
                ["Colors", "Clouds", "Snow", "Fog"],
                "Colors",
                "The passage says colors fill the whole sky.",
            ),
        ],
    ),
    PassageSeed(
        title="My Pet Cat",
        body=(
            "Sam has a small cat. Her name is Tuffy. "
            "Tuffy has soft white fur. She sleeps most of the day. "
            "Tuffy loves warm sun spots. Sam feeds her fish and milk. "
            "Tuffy purrs when Sam pets her. At night she curls up close. "
            "Sam reads next to Tuffy. They both fall asleep soon."
        ),
        difficulty_rank=3,
        takeaway="Taking care of a pet brings comfort to both the pet and its owner.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What kind of pet does Sam have?",
                ["A cat", "A dog", "A bird", "A fish"],
                "A cat",
                "The passage says Sam has a small cat.",
            ),
            QuestionSeed(
                "literal_recall",
                "What is the cat's name?",
                ["Tuffy", "Milo", "Coco", "Whiskers"],
                "Tuffy",
                "The passage says her name is Tuffy.",
            ),
            QuestionSeed(
                "literal_recall",
                "What color is Tuffy's fur?",
                ["Soft white", "Jet black", "Bright orange", "Light grey"],
                "Soft white",
                "The passage says Tuffy has soft white fur.",
            ),
            QuestionSeed(
                "literal_recall",
                "How much does Tuffy sleep?",
                ["A lot", "A little", "Not at all", "Only twice"],
                "A lot",
                "The passage says she sleeps most of the day.",
            ),
            QuestionSeed(
                "literal_recall",
                "What does Tuffy love?",
                ["Warm spots", "Cold water", "Loud noise", "Long walks"],
                "Warm spots",
                "The passage says Tuffy loves warm sun spots.",
            ),
            QuestionSeed(
                "literal_recall",
                "What does Sam feed Tuffy?",
                ["Fish and milk", "Rice and beans", "Bread and jam", "Meat and eggs"],
                "Fish and milk",
                "The passage says Sam feeds her fish and milk.",
            ),
            QuestionSeed(
                "literal_recall",
                "What does Sam do with Tuffy at night?",
                ["Reads nearby", "Sings songs", "Plays games", "Takes walks"],
                "Reads nearby",
                "The passage says Sam reads next to Tuffy.",
            ),
        ],
    ),
    PassageSeed(
        title="The Big Kite",
        body=(
            "Raj got a new kite. It was red and gold. "
            "He ran to the park. The wind was strong today. "
            "Raj let the string go. His kite flew up high. "
            "It danced above the trees. Raj held the string tight. "
            "Other kids came to watch. Raj smiled at his kite."
        ),
        difficulty_rank=4,
        takeaway="Trying something new, like flying a kite, can bring great joy.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did Raj get?",
                ["A new kite", "A toy car", "A soccer ball", "A puzzle"],
                "A new kite",
                "The passage says Raj got a new kite.",
            ),
            QuestionSeed(
                "literal_recall",
                "What colors was the kite?",
                ["Red and gold", "Blue and white", "Green and black", "Pink and silver"],
                "Red and gold",
                "The passage says it was red and gold.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where did Raj run to?",
                ["The park", "The beach", "The store", "The school"],
                "The park",
                "The passage says he ran to the park.",
            ),
            QuestionSeed(
                "literal_recall",
                "How was the wind that day?",
                ["Strong", "Weak", "Cold", "Still"],
                "Strong",
                "The passage says the wind was strong today.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the kite dance above?",
                ["The trees", "The houses", "The clouds", "The hills"],
                "The trees",
                "The passage says it danced above the trees.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where did the kite fly?",
                ["Up high", "Down low", "Far away", "Very fast"],
                "Up high",
                "The passage says his kite flew up high.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who came to watch Raj's kite?",
                ["Other kids", "His mom", "His dad", "Nobody"],
                "Other kids",
                "The passage says other kids came to watch.",
            ),
        ],
    ),
    PassageSeed(
        title="Wash Your Hands",
        body=(
            "Neha eats her lunch daily. First she goes to the sink. "
            "She turns on the tap. Water flows on her hands. "
            "She rubs soap on her palms. Germs go into the drain. "
            "Neha dries her hands well. Now her hands are clean."
        ),
        difficulty_rank=5,
        takeaway="Washing hands removes germs and keeps you healthy.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What does Neha do daily?",
                ["Eats lunch", "Runs fast", "Reads books", "Sleeps late"],
                "Eats lunch",
                "The passage says Neha eats her lunch daily.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where does she go first?",
                ["Sink", "Bed", "Door", "Yard"],
                "Sink",
                "The passage says she first goes to the sink.",
            ),
            QuestionSeed(
                "literal_recall",
                "What does she turn on?",
                ["Tap", "Light", "Fan", "Radio"],
                "Tap",
                "The passage says she turns on the tap.",
            ),
            QuestionSeed(
                "literal_recall",
                "What flows on her hands?",
                ["Water", "Oil", "Sand", "Milk"],
                "Water",
                "The passage says water flows on her hands.",
            ),
            QuestionSeed(
                "literal_recall",
                "What does she rub on her palms?",
                ["Soap", "Oil", "Mud", "Sugar"],
                "Soap",
                "The passage says she rubs soap on her palms.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where do germs go?",
                ["Drain", "Sink", "Cup", "Bowl"],
                "Drain",
                "The passage says germs go into the drain.",
            ),
            QuestionSeed(
                "literal_recall",
                "How are her hands at the end?",
                ["Clean", "Dirty", "Wet only", "Cold"],
                "Clean",
                "The passage says her hands are clean at the end.",
            ),
        ],
    ),
    PassageSeed(
        title="A Trip to the Zoo",
        body=(
            "Last Sunday, Aarav went to the zoo. He saw a tall spotted giraffe by the gate. "
            "The giraffe reached up to eat green leaves. Nearby, bright parrots sat on a wooden branch. "
            "Aarav watched two monkeys swing and chase each other. A lazy lion slept under a shady tree. "
            "Aarav's mother bought him a cold lemon drink. They stopped to feed some hungry ducks bread. "
            "Aarav loved the striped tigers most. He asked his mother if they could return soon."
        ),
        difficulty_rank=6,
        takeaway="Visiting a zoo helps us learn about many different animals.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Where did Aarav go last Sunday?",
                ["The zoo", "The park", "The beach", "The mall"],
                "The zoo",
                "The passage says Aarav went to the zoo.",
            ),
            QuestionSeed(
                "literal_recall",
                "What animal did he see by the gate?",
                ["A giraffe", "A lion", "A tiger", "A monkey"],
                "A giraffe",
                "The passage says he saw a spotted giraffe by the gate.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the giraffe eat?",
                ["Green leaves", "Red apples", "Fresh grass", "Small fish"],
                "Green leaves",
                "The passage says the giraffe reached up to eat green leaves.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where did the parrots sit?",
                ["Wooden branch", "Stone wall", "Metal cage", "Tall grass"],
                "Wooden branch",
                "The passage says parrots sat on a wooden branch.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the monkeys do?",
                ["Swing and chase", "Sleep all day", "Eat leaves", "Climb rocks"],
                "Swing and chase",
                "The passage says two monkeys swing and chase each other.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where did the lion sleep?",
                ["Under a tree", "Near the gate", "In a cave", "By the pond"],
                "Under a tree",
                "The passage says a lazy lion slept under a shady tree.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Aarav feed the ducks?",
                ["Bread", "Corn", "Rice", "Fish"],
                "Bread",
                "The passage says they stopped to feed hungry ducks bread.",
            ),
        ],
    ),
    PassageSeed(
        title="The New Bicycle",
        body=(
            "Priya got a shiny new bicycle as a gift. It had a bright red frame and silver wheels. "
            "Her father helped her ride in the park. At first, Priya wobbled and fell. "
            "She pushed the pedals harder and found her balance. Soon Priya could ride in a line. "
            "She waved happily at her father from afar. Her friends cheered when she circled the whole park. "
            "Priya wanted to ride every single evening. She parked her bicycle safely near the door."
        ),
        difficulty_rank=7,
        takeaway="Practice and patience help us learn new skills.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did Priya get as a gift?",
                ["A bicycle", "A scooter", "A skateboard", "A tricycle"],
                "A bicycle",
                "The passage says Priya got a shiny new bicycle.",
            ),
            QuestionSeed(
                "literal_recall",
                "What color was the frame?",
                ["Bright red", "Deep blue", "Dark green", "Light pink"],
                "Bright red",
                "The passage says it had a bright red frame.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who helped Priya ride?",
                ["Her father", "Her mother", "Her sister", "Her teacher"],
                "Her father",
                "The passage says her father helped her ride.",
            ),
            QuestionSeed(
                "literal_recall",
                "What happened to Priya at first?",
                ["She wobbled", "She fell asleep", "She cried", "She stopped"],
                "She wobbled",
                "The passage says Priya wobbled and fell.",
            ),
            QuestionSeed(
                "literal_recall",
                "What helped Priya find her balance?",
                ["Pushing harder", "Sitting still", "Going slow", "Closing her eyes"],
                "Pushing harder",
                "The passage says she pushed the pedals harder and found her balance.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did Priya wave at her father?",
                ["Happily", "Sadly", "Angrily", "Quietly"],
                "Happily",
                "The passage says she waved happily at her father.",
            ),
            QuestionSeed(
                "literal_recall",
                "How often did Priya want to ride?",
                ["Every evening", "Once a week", "Only Sundays", "Never again"],
                "Every evening",
                "The passage says Priya wanted to ride every single evening.",
            ),
        ],
    ),
    PassageSeed(
        title="Baking Cookies with Grandma",
        body=(
            "One morning, Ravi visited his grandma at her house. They planned to bake cookies that day. "
            "Grandma mixed flour, sugar, and soft butter first. Ravi cracked two eggs into the mixing bowl. "
            "They rolled small balls of dough with their hands. Grandma placed the cookies onto a metal tray. "
            "The kitchen smelled sweet as the cookies baked. Ravi watched closely through the warm oven glass. "
            "Finally, they ate warm cookies with cold milk. Ravi wanted to bake again next weekend."
        ),
        difficulty_rank=8,
        takeaway="Cooking together with family creates happy memories.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Whose house did Ravi visit?",
                ["Grandma", "Uncle", "Cousin", "Friend"],
                "Grandma",
                "The passage says Ravi visited his grandma at her house.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did they plan to bake?",
                ["Cookies", "Bread", "Cake", "Pie"],
                "Cookies",
                "The passage says they planned to bake cookies that day.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Grandma mix first?",
                ["Flour and sugar", "Milk and eggs", "Rice and salt", "Oil and honey"],
                "Flour and sugar",
                "The passage says Grandma mixed flour, sugar, and soft butter first.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Ravi crack into the bowl?",
                ["Two eggs", "One egg", "Three eggs", "No eggs"],
                "Two eggs",
                "The passage says Ravi cracked two eggs into the mixing bowl.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did they roll with their hands?",
                ["Small balls", "Long ropes", "Flat sheets", "Big blocks"],
                "Small balls",
                "The passage says they rolled small balls of dough.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where did Grandma place the cookies?",
                ["A metal tray", "A glass bowl", "A paper plate", "A wooden box"],
                "A metal tray",
                "The passage says Grandma placed the cookies onto a metal tray.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did they drink with the cookies?",
                ["Cold milk", "Hot tea", "Orange juice", "Warm water"],
                "Cold milk",
                "The passage says they ate warm cookies with cold milk.",
            ),
        ],
    ),
    PassageSeed(
        title="A Day at the Farm",
        body=(
            "Last week, Meera and her brother visited a farm. A kind farmer showed them his big fields. "
            "They saw fluffy sheep resting under a tree. Meera fed corn to some brown hens. "
            "Her brother tried milking a spotted cow. They rode slowly on a cart pulled by horses. "
            "The farmer let them pick red apples. Meera took warm eggs from a wooden coop. "
            "They watched baby goats jump around the yard. Meera and her brother wanted to visit again soon."
        ),
        difficulty_rank=9,
        takeaway="Farms are full of animals and hard work that gives us food.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Where did Meera and her brother go?",
                ["A farm", "A zoo", "A market", "A beach"],
                "A farm",
                "The passage says they visited a farm.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who showed them around the fields?",
                ["The farmer", "The teacher", "Their father", "A neighbor"],
                "The farmer",
                "The passage says a kind farmer showed them his fields.",
            ),
            QuestionSeed(
                "literal_recall",
                "What were the sheep doing?",
                ["Resting", "Jumping", "Swimming", "Flying"],
                "Resting",
                "The passage says sheep were resting under a tree.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Meera feed the hens?",
                ["Corn", "Rice", "Bread", "Seeds"],
                "Corn",
                "The passage says Meera fed corn to some hens.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did her brother try to do?",
                ["Milk a cow", "Ride a horse", "Feed a pig", "Catch a hen"],
                "Milk a cow",
                "The passage says her brother tried milking a spotted cow.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did they ride on the cart?",
                ["Slowly", "Quickly", "Loudly", "Backwards"],
                "Slowly",
                "The passage says they rode slowly on a cart.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did they pick from the farm?",
                ["Red apples", "Green pears", "Ripe mangoes", "Yellow corn"],
                "Red apples",
                "The passage says the farmer let them pick red apples.",
            ),
        ],
    ),
    PassageSeed(
        title="The School Picnic",
        body=(
            "Our class went on a picnic to a park. Teacher Anu packed snacks, fruit, and juice boxes. "
            "We spread a blanket under a shady tree. Some kids played tag near the slide. "
            "Others sat quietly and drew birds and trees. My best friend and I shared mango slices. "
            "We played a game of hide and seek. Then it started to drizzle a bit. "
            "We quickly packed our bags and ran for cover. The kids sang and laughed on the bus."
        ),
        difficulty_rank=10,
        takeaway="Outdoor trips with friends are fun even when the weather changes.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Where did the class go?",
                ["A park", "A market", "A beach", "A farm"],
                "A park",
                "The passage says the class went on a picnic to a park.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who packed the snacks?",
                ["Teacher Anu", "The principal", "Meera's mom", "A classmate"],
                "Teacher Anu",
                "The passage says Teacher Anu packed snacks, fruit, and juice.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where did they spread the blanket?",
                ["Under a tree", "Near the gate", "By the pond", "On the grass"],
                "Under a tree",
                "The passage says they spread a blanket under a shady tree.",
            ),
            QuestionSeed(
                "literal_recall",
                "What game did some kids play near the slide?",
                ["Tag", "Hopscotch", "Cricket", "Chess"],
                "Tag",
                "The passage says some kids played tag near the slide.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did others draw?",
                ["Birds and trees", "Cars and roads", "Flowers and bees", "Houses and hills"],
                "Birds and trees",
                "The passage says others sat quietly and drew birds and trees.",
            ),
            QuestionSeed(
                "literal_recall",
                "What fruit slices did friends share?",
                ["Mango", "Apple", "Banana", "Grape"],
                "Mango",
                "The passage says my best friend and I shared mango slices.",
            ),
            QuestionSeed(
                "literal_recall",
                "What happened when it began to drizzle?",
                ["Ran for cover", "Kept playing", "Opened umbrellas", "Went swimming"],
                "Ran for cover",
                "The passage says they quickly packed their bags and ran for cover.",
            ),
        ],
    ),
    PassageSeed(
        title="The Lost Kitten",
        body=(
            "Priya heard a soft meow near her garden gate. "
            "She found a tiny grey kitten hiding behind a bush. "
            "The kitten looked hungry, cold, and very scared. "
            "Priya gently picked it up, held it close, and named her Coco. "
            "She brought the kitten inside and gave it warm milk. "
            "The kitten drank quickly and then curled up to sleep. "
            "Priya made posters to find the kitten's owner. "
            "A week later, no one had come to claim it. "
            "Priya's family decided to keep the kitten forever."
        ),
        difficulty_rank=11,
        takeaway="A little kindness can turn a scared stranger into a beloved friend.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did Priya hear near her garden gate?",
                ["A soft meow", "A loud bark", "A bird chirping", "A door creak"],
                "A soft meow",
                "The passage says Priya heard a soft meow near her garden gate.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where was the kitten hiding?",
                ["Behind a bush", "Under a car", "Inside a box", "Near the pond"],
                "Behind a bush",
                "The passage says she found the kitten hiding behind a bush.",
            ),
            QuestionSeed(
                "literal_recall",
                "What name did Priya give the kitten?",
                ["Coco", "Tuffy", "Milo", "Snowy"],
                "Coco",
                "The passage says Priya named her Coco.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Priya do right after bringing the kitten inside?",
                ["Gave it warm milk", "Made posters", "Called her family", "Went to sleep"],
                "Gave it warm milk",
                "The passage says she brought the kitten inside and gave it warm milk.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after Priya made posters?",
                ["No one claimed the kitten", "The kitten ran away", "Someone took the kitten", "The kitten got sick"],
                "No one claimed the kitten",
                "The passage says a week later, no one had come to claim it.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'claim' mean?",
                ["Say it belongs to you", "Give something away", "Clean something well", "Hide something safely"],
                "Say it belongs to you",
                "Someone would 'claim' the kitten by saying it is theirs.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Priya's family decide to do?",
                ["Keep the kitten", "Give it away", "Take it to a shelter", "Find its owner again"],
                "Keep the kitten",
                "The passage says Priya's family decided to keep the kitten forever.",
            ),
        ],
    ),
    PassageSeed(
        title="A Trip to the Library",
        body=(
            "On Saturday, Karan visited the public library with his sister. "
            "The library was quiet, calm, and full of tall shelves. "
            "Karan searched for books about space and distant planets. "
            "His sister picked a colorful book about ocean animals. "
            "A friendly library helper helped them find the right sections. "
            "They sat quietly at a wooden table and read for an hour. "
            "Karan borrowed three books using his shiny new library card. "
            "Before leaving, they returned some books from last month. "
            "Karan promised to visit the library again next weekend."
        ),
        difficulty_rank=12,
        takeaway="Libraries open the door to new worlds through books.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Who did Karan visit the library with?",
                ["His sister", "His mother", "His friend", "His teacher"],
                "His sister",
                "The passage says Karan visited the library with his sister.",
            ),
            QuestionSeed(
                "literal_recall",
                "What books did Karan search for?",
                ["Books about space", "Books about animals", "Books about cooking", "Books about sports"],
                "Books about space",
                "The passage says Karan searched for books about space and distant planets.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did his sister pick?",
                ["A book about ocean animals", "A book about space", "A book about cooking", "A book about sports"],
                "A book about ocean animals",
                "The passage says his sister picked a colorful book about ocean animals.",
            ),
            QuestionSeed(
                "sequencing",
                "What did they do after finding the right sections?",
                ["Sat down and read", "Borrowed books", "Left the library", "Returned old books"],
                "Sat down and read",
                "The passage says they sat quietly at a wooden table and read.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Karan do before leaving the library?",
                ["Returned old books", "Searched for space books", "Met his sister", "Read for an hour"],
                "Returned old books",
                "The passage says before leaving, they returned some books from last month.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'sections' mean?",
                ["Parts of the library", "Types of books", "Names of shelves", "Library workers"],
                "Parts of the library",
                "The 'right sections' means the correct parts of the library where books are kept.",
            ),
            QuestionSeed(
                "literal_recall",
                "How many books did Karan borrow?",
                ["Three", "Two", "Four", "One"],
                "Three",
                "The passage says Karan borrowed three books.",
            ),
        ],
    ),
    PassageSeed(
        title="The School Sports Day",
        body=(
            "Every year, our school holds a big sports day event. "
            "Students wear colorful team shirts and cheer loudly for friends. "
            "Meera ran the fastest in the two hundred meter race. "
            "Her friend Dev won first place in the long jump. "
            "Teachers planned fun relay races for younger students too. "
            "The tug of war match was noisy and full of energy. "
            "Everyone received a small medal just for trying their best. "
            "At the end, the winning team lifted a shiny trophy. "
            "Meera said sports day was her favorite day of the year."
        ),
        difficulty_rank=13,
        takeaway="Trying your best matters as much as winning.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What does the school hold every year?",
                ["A sports day", "A science fair", "A music concert", "A book fair"],
                "A sports day",
                "The passage says the school holds a big sports day event every year.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Meera do in the race?",
                ["Ran the fastest", "Came in last", "Fell down", "Did not run"],
                "Ran the fastest",
                "The passage says Meera ran the fastest in the two hundred meter race.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Dev win?",
                ["First place in long jump", "Second place in the race", "A medal for singing", "Nothing at all"],
                "First place in long jump",
                "The passage says Dev won first place in the long jump.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after the tug of war match?",
                ["Everyone received a medal", "Meera ran her race", "Dev did the long jump", "Teachers planned relay races"],
                "Everyone received a medal",
                "The passage says after the tug of war, everyone received a small medal.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'energy' mean?",
                ["Excitement and activity", "Quiet and calm", "Sadness and tears", "Sleep and rest"],
                "Excitement and activity",
                "The tug of war being 'full of energy' means full of excitement and activity.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the winning team lift at the end?",
                ["A shiny trophy", "A gold medal", "A big flag", "A ribbon"],
                "A shiny trophy",
                "The passage says the winning team lifted a shiny trophy.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Meera say about sports day?",
                ["It was her favorite day", "It was too tiring", "It was boring", "It was too long"],
                "It was her favorite day",
                "The passage says Meera said sports day was her favorite day of the year.",
            ),
        ],
    ),
    PassageSeed(
        title="Growing a Garden",
        body=(
            "Grandpa decided to grow a small veggie garden this spring. "
            "He dug the soil and removed every stone and weed. "
            "Grandpa planted tomato seeds, carrot seeds, and pepper seeds with care. "
            "Every morning, he watered the plants each day without fail. "
            "Slowly, tiny green shoots began to poke through the soil. "
            "Grandpa built a fence to keep hungry rabbits away. "
            "After many weeks, the tomato plants grew tall and strong. "
            "Bright red tomatoes finally appeared among the green leaves. "
            "Grandpa shared his fresh veggies with all his friends. "
            "It gave him great joy each day."
        ),
        difficulty_rank=14,
        takeaway="Patience and daily care help small things grow into something wonderful.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did Grandpa decide to grow?",
                ["A veggie garden", "A flower garden", "A fruit orchard", "A herb patch"],
                "A veggie garden",
                "The passage says Grandpa decided to grow a small veggie garden.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Grandpa do before planting the seeds?",
                ["Removed stones and weeds", "Built a fence", "Watered the plants", "Shared his veggies"],
                "Removed stones and weeds",
                "The passage says he dug the soil and removed every stone and weed before planting.",
            ),
            QuestionSeed(
                "literal_recall",
                "What seeds did Grandpa plant?",
                ["Tomato, carrot, and pepper", "Corn, beans, and peas", "Rice, wheat, and oats", "Onion, garlic, and chili"],
                "Tomato, carrot, and pepper",
                "The passage says Grandpa planted tomato seeds, carrot seeds, and pepper seeds.",
            ),
            QuestionSeed(
                "literal_recall",
                "Why did Grandpa build a fence?",
                ["To keep rabbits away", "To keep birds away", "To block the sun", "To mark the garden"],
                "To keep rabbits away",
                "The passage says Grandpa built a fence to keep hungry rabbits away.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after the tomato plants grew tall?",
                ["Red tomatoes appeared", "Grandpa planted seeds", "He built a fence", "He dug the soil"],
                "Red tomatoes appeared",
                "The passage says bright red tomatoes finally appeared among the green leaves.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'shoots' mean?",
                ["New plant growth", "Loud noises", "Garden tools", "Falling leaves"],
                "New plant growth",
                "'Tiny green shoots' poking through soil means new plant growth.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Grandpa do with his fresh veggies?",
                ["Shared them with friends", "Sold them at a market", "Kept them all himself", "Threw them away"],
                "Shared them with friends",
                "The passage says Grandpa shared his fresh veggies with all his friends.",
            ),
        ],
    ),
    PassageSeed(
        title="The Broken Toy",
        body=(
            "Arjun's favorite toy robot suddenly stopped working one evening. "
            "He pressed every button, but nothing happened at all. "
            "Arjun felt upset and worried his robot was broken forever. "
            "His older sister offered to look inside the robot gently. "
            "She found that the battery was old and totally dead. "
            "Arjun waited quietly and watched her work with care. "
            "Together, they walked to the store to buy a new battery. "
            "Back home, she replaced the battery with steady hands. "
            "The robot's lights blinked, and it began to move again. "
            "Arjun hugged his sister and thanked her for the help."
        ),
        difficulty_rank=15,
        takeaway="Asking for help can turn a problem into something you solve together.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What happened to Arjun's toy robot?",
                ["It stopped working", "It got lost", "It broke in half", "It was stolen"],
                "It stopped working",
                "The passage says Arjun's toy robot suddenly stopped working.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did Arjun feel about his robot?",
                ["Upset and worried", "Happy and excited", "Angry at his sister", "Bored and sleepy"],
                "Upset and worried",
                "The passage says Arjun felt upset and worried his robot was broken forever.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Arjun's sister find inside the robot?",
                ["A dead battery", "A loose wire", "A broken button", "Nothing wrong"],
                "A dead battery",
                "The passage says she found that the battery was old and totally dead.",
            ),
            QuestionSeed(
                "sequencing",
                "What did they do after finding the dead battery?",
                ["Walked to the store", "Hugged each other", "Threw the robot away", "Pressed the buttons again"],
                "Walked to the store",
                "The passage says together, they walked to the store to buy a new battery.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after the battery was replaced?",
                ["The robot began to move", "Arjun felt more upset", "The sister left the room", "They went back to the store"],
                "The robot began to move",
                "The passage says the robot's lights blinked, and it began to move again.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'steady' mean?",
                ["Calm and careful", "Fast and rushed", "Shaky and nervous", "Loud and rough"],
                "Calm and careful",
                "'Steady hands' means hands that are calm and careful, not shaky.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Arjun do at the end?",
                ["Hugged his sister", "Cried loudly", "Ran outside", "Called his mother"],
                "Hugged his sister",
                "The passage says Arjun hugged his sister and thanked her for the help.",
            ),
        ],
    ),
    PassageSeed(
        title="A Visit to the Dentist",
        body=(
            "Sara felt nervous about her first visit to the dentist. "
            "Her mother held her hand as they entered the office. "
            "The dentist smiled kindly and told her what she would do. "
            "Sara sat back in a big chair with a bright light. "
            "The dentist counted her teeth and checked for any cavities. "
            "She cleaned Sara's teeth gently using a small soft brush. "
            "Sara learned the best way to brush and floss daily. "
            "The whole visit took only about twenty quiet minutes. "
            "Sara felt proud and no longer scared at all. "
            "Sara left the office proudly wearing a new tooth sticker."
        ),
        difficulty_rank=16,
        takeaway="Facing something scary often feels much easier once it is over.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "How did Sara feel before her visit?",
                ["Nervous", "Excited", "Angry", "Bored"],
                "Nervous",
                "The passage says Sara felt nervous about her first visit to the dentist.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who held Sara's hand as they entered?",
                ["Her mother", "Her father", "Her sister", "Her friend"],
                "Her mother",
                "The passage says her mother held her hand as they entered the office.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the dentist check for?",
                ["Cavities", "Broken bones", "A fever", "A sore throat"],
                "Cavities",
                "The passage says the dentist counted her teeth and checked for any cavities.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the dentist do after counting Sara's teeth?",
                ["Cleaned her teeth", "Gave her a sticker", "Sent her home", "Took a photo"],
                "Cleaned her teeth",
                "The passage says she cleaned Sara's teeth gently after checking for cavities.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Sara learn at the dentist?",
                ["How to brush and floss", "How to fix teeth", "How to count teeth", "How to clean the office"],
                "How to brush and floss",
                "The passage says Sara learned the best way to brush and floss daily.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'proudly' mean?",
                ["Feeling pleased with yourself", "Feeling scared and shy", "Feeling tired and sleepy", "Feeling angry and upset"],
                "Feeling pleased with yourself",
                "Sara left 'proudly,' meaning she felt pleased with herself.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Sara receive right before leaving?",
                ["A tooth sticker", "A new toothbrush", "A candy treat", "A balloon"],
                "A tooth sticker",
                "The passage says Sara left the office proudly wearing a new tooth sticker.",
            ),
        ],
    ),
    PassageSeed(
        title="The Class Play",
        body=(
            "Our teacher chose a fairy tale for the class play. "
            "Rohan worked on his lines every single night before bedtime. "
            "He played the brave and kind knight who saves a small village. "
            "Costumes were bright, colorful, and made by helpful parents. "
            "On the big day, the school hall filled with proud families. "
            "Rohan's whole family cheered loudly from the very front row. "
            "Rohan felt nervous standing behind the heavy stage curtain. "
            "When the curtain opened, he recalled every single line well. "
            "The audience clapped loudly when the knight defeated the dragon. "
            "Rohan bowed happily as everyone cheered for the whole cast."
        ),
        difficulty_rank=17,
        takeaway="Hard work and practice help nervousness turn into confidence.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did the teacher choose for the class play?",
                ["A fairy tale", "A history story", "A science project", "A sports event"],
                "A fairy tale",
                "The passage says our teacher chose a fairy tale for the class play.",
            ),
            QuestionSeed(
                "literal_recall",
                "What role did Rohan play?",
                ["A brave knight", "A wise king", "A funny jester", "A sleepy dragon"],
                "A brave knight",
                "The passage says Rohan played the brave and kind knight who saves a village.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who made the costumes?",
                ["Helpful parents", "The teachers", "The students", "A costume shop"],
                "Helpful parents",
                "The passage says costumes were made by helpful parents.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Rohan feel right before the curtain opened?",
                ["Nervous", "Proud", "Sleepy", "Angry"],
                "Nervous",
                "The passage says Rohan felt nervous standing behind the heavy stage curtain.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after the knight defeated the dragon?",
                ["The audience clapped loudly", "The curtain opened", "Rohan felt nervous", "The play began"],
                "The audience clapped loudly",
                "The passage says the audience clapped loudly when the knight defeated the dragon.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'defeated' mean?",
                ["Won against", "Ran away from", "Made friends with", "Talked to"],
                "Won against",
                "The knight 'defeated' the dragon, meaning he won against it.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did Rohan bow at the end?",
                ["Happily", "Sadly", "Angrily", "Quietly"],
                "Happily",
                "The passage says Rohan bowed happily as everyone cheered.",
            ),
        ],
    ),
    PassageSeed(
        title="Saving Water at Home",
        body=(
            "Our teacher taught us why saving water matters for everyone. "
            "She said that clean water is limited around the world. "
            "At home, I started turning off the tap while brushing. "
            "My family fixed a leaky faucet that dripped all night. "
            "We began saving rainfall in a large plastic barrel outside. "
            "Mom now uses that water to feed our garden plants. "
            "We also take shorter showers to avoid wasting extra water. "
            "Small changes like these can save a lot of water. "
            "Saving water helps protect our planet's future. "
            "Every small action makes a big change. "
            "Everyone on our street is trying these simple habits together now."
        ),
        difficulty_rank=18,
        takeaway="Small daily habits, shared by everyone, can protect something precious.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did the teacher teach the class about?",
                ["Saving water", "Saving electricity", "Growing plants", "Recycling paper"],
                "Saving water",
                "The passage says our teacher taught us why saving water matters.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the family fix?",
                ["A leaky faucet", "A broken window", "A cracked wall", "A slow drain"],
                "A leaky faucet",
                "The passage says my family fixed a leaky faucet that dripped all night.",
            ),
            QuestionSeed(
                "literal_recall",
                "What do they collect in the barrel?",
                ["Rainfall", "Tap water", "Pool water", "River water"],
                "Rainfall",
                "The passage says we began saving rainfall in a large plastic barrel.",
            ),
            QuestionSeed(
                "sequencing",
                "What does Mom do with the collected water?",
                ["Feeds the garden plants", "Washes the car", "Fills the pool", "Cleans the floor"],
                "Feeds the garden plants",
                "The passage says Mom now uses that water to feed our garden plants.",
            ),
            QuestionSeed(
                "literal_recall",
                "What else does the family do to save water?",
                ["Take shorter showers", "Take longer baths", "Wash dishes twice", "Water the lawn more"],
                "Take shorter showers",
                "The passage says we also take shorter showers to avoid wasting extra water.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'limited' mean?",
                ["Not available in large amounts", "Free for everyone", "Found everywhere easily", "Always increasing"],
                "Not available in large amounts",
                "'Limited' water means it is not available in large, endless amounts.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who else is trying these water habits now?",
                ["The whole street", "Just the family", "No one else", "Only the teacher"],
                "The whole street",
                "The passage says everyone on our street is trying these simple habits together now.",
            ),
        ],
    ),
    PassageSeed(
        title="The New Neighbor",
        body=(
            "A new family moved into the house next door last month. "
            "Their daughter Zara was the same age as me exactly. "
            "At first, Zara seemed shy and did not talk much. "
            "I invited her to play in our garden one sunny day. "
            "We found we both loved drawing colorful pictures of animals. "
            "Slowly, Zara became more at ease and started smiling more. "
            "We often ride bikes together after school ends. "
            "Zara makes every day feel more fun. "
            "We now walk to school together nearly every morning. "
            "Zara brought me to meet her cousins during the summer holidays. "
            "I am grateful that such a good friend lives so close."
        ),
        difficulty_rank=19,
        takeaway="Giving a shy new friend time and kindness can grow into a close friendship.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Who moved in next door?",
                ["A new family", "A new teacher", "An old friend", "A shopkeeper"],
                "A new family",
                "The passage says a new family moved into the house next door.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did Zara seem at first?",
                ["Shy", "Loud", "Angry", "Sleepy"],
                "Shy",
                "The passage says at first, Zara seemed shy and did not talk much.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after the narrator invited Zara to play?",
                ["They found they both loved drawing", "Zara moved away", "Zara stopped talking", "They stopped being friends"],
                "They found they both loved drawing",
                "The passage says we found we both loved drawing colorful pictures of animals.",
            ),
            QuestionSeed(
                "literal_recall",
                "What do they do together after school?",
                ["Ride bikes", "Play video games", "Do homework", "Watch movies"],
                "Ride bikes",
                "The passage says we often ride bikes together after school ends.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who did Zara introduce during the summer holidays?",
                ["Her cousins", "Her teacher", "Her neighbors", "Her grandparents"],
                "Her cousins",
                "The passage says Zara brought me to meet her cousins during the summer holidays.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'at ease' mean?",
                ["Comfortable and relaxed", "Nervous and shy", "Tired and sleepy", "Angry and upset"],
                "Comfortable and relaxed",
                "Zara became 'more at ease,' meaning more comfortable and relaxed.",
            ),
            QuestionSeed(
                "literal_recall",
                "How does the narrator feel about Zara at the end?",
                ["Grateful", "Annoyed", "Confused", "Worried"],
                "Grateful",
                "The passage says I am grateful that such a good friend lives so close.",
            ),
        ],
    ),
    PassageSeed(
        title="A Camping Adventure",
        body=(
            "Our family packed the car for a weekend camping trip. "
            "We drove for many hours until we reached a quiet forest. "
            "Dad set up a large tent near a clear stream. "
            "We gathered dry sticks and built a small campfire together. "
            "Mom cooked warm soup while we watched the orange flames. "
            "The warm campfire kept us cozy and safe all evening. "
            "We told funny stories until it got quite late. "
            "At night, we saw many bright stars above us. "
            "An owl hooted softly nearby in the dark woods. "
            "The next morning, we hiked up a steep rocky trail. "
            "Tired but happy, we packed up and drove safely home."
        ),
        difficulty_rank=20,
        takeaway="Simple moments in nature can create a family's happiest memories.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did the family pack the car for?",
                ["A camping trip", "A beach trip", "A city trip", "A school trip"],
                "A camping trip",
                "The passage says our family packed the car for a weekend camping trip.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Dad do after they reached the forest?",
                ["Set up the tent", "Cooked soup", "Told stories", "Hiked the trail"],
                "Set up the tent",
                "The passage says Dad set up a large tent near a clear stream after they arrived.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Mom cook?",
                ["Warm soup", "Fried rice", "Grilled fish", "Pasta"],
                "Warm soup",
                "The passage says Mom cooked warm soup while we watched the orange flames.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did they see at night?",
                ["Many bright stars", "A full moon", "Fireworks", "Flying birds"],
                "Many bright stars",
                "The passage says at night, we saw many bright stars above us.",
            ),
            QuestionSeed(
                "literal_recall",
                "What animal hooted in the woods?",
                ["An owl", "A wolf", "A fox", "A bear"],
                "An owl",
                "The passage says an owl hooted softly nearby in the dark woods.",
            ),
            QuestionSeed(
                "sequencing",
                "What did they do the next morning?",
                ["Hiked up a rocky trail", "Set up the tent", "Told funny stories", "Drove to the forest"],
                "Hiked up a rocky trail",
                "The passage says the next morning, we hiked up a steep rocky trail.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'cozy' mean?",
                ["Warm and comfortable", "Cold and wet", "Dark and scary", "Loud and busy"],
                "Warm and comfortable",
                "The campfire kept them 'cozy,' meaning warm and comfortable.",
            ),
        ],
    ),
    PassageSeed(
        title="The Museum Trip",
        body=(
            "Last Friday, our class went on a trip to the city museum. "
            "Our friendly guide showed us ancient clay pots that were thousands of years old. "
            "In one big room, we saw a giant model of a dinosaur skeleton. "
            "Sam asked the guide how such old bones stayed safe for so long. "
            "The guide said that special glass cases keep fragile old objects safe. "
            "Next, we walked into a room full of bright, colorful paintings. "
            "One large painting showed a busy village market from long ago. "
            "Our teacher asked us to sketch our favorite object before we left. "
            "Everyone left the museum feeling excited to learn even more about history."
        ),
        difficulty_rank=21,
        takeaway="Old objects in museums help us understand how people lived long ago.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Where did the class go on their trip?",
                ["The city museum", "The science center", "The art gallery", "The local zoo"],
                "The city museum",
                "The passage says the class went on a trip to the city museum.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the guide show them first?",
                ["Ancient clay pots", "A dinosaur skeleton", "Colorful paintings", "A village market painting"],
                "Ancient clay pots",
                "The passage says the guide showed them ancient clay pots first.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why do glass cases protect the museum objects?",
                ["Because the objects are fragile and old", "Because the objects are too big", "Because visitors might buy them", "Because the room is too bright"],
                "Because the objects are fragile and old",
                "The passage says glass cases keep fragile old objects safe.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the class see right after the dinosaur skeleton?",
                ["A room of paintings", "The clay pots", "The village market", "Their teacher's sketch"],
                "A room of paintings",
                "The passage says next, they walked into a room full of paintings.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the large painting show?",
                ["A busy village market", "A dinosaur skeleton", "A city street", "A quiet forest"],
                "A busy village market",
                "The passage says one large painting showed a busy village market.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'fragile' mean?",
                ["Easily broken", "Very heavy", "Extremely old", "Brightly colored"],
                "Easily broken",
                "'Fragile old objects' means objects that break easily and must be protected.",
            ),
            QuestionSeed(
                "inference",
                "Why did the teacher ask students to sketch an object?",
                ["To help them remember what they saw", "To test their drawing skills", "To decorate the museum", "To keep them quiet"],
                "To help them remember what they saw",
                "Sketching a favorite object helps students remember and reflect on their visit.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did everyone feel leaving the museum?",
                ["Excited to learn more", "Tired and bored", "Confused and lost", "Hungry for lunch"],
                "Excited to learn more",
                "The passage says everyone left the museum feeling excited to learn more about history.",
            ),
        ],
    ),
    PassageSeed(
        title="Riya Plants a Tree",
        body=(
            "Riya's whole class was chosen to plant new trees for the school garden. "
            "Each student received a small green sapling and a wooden shovel. "
            "Riya dug a hole exactly as deep as her teacher had shown her. "
            "She placed her sapling gently and pressed soft brown soil around its roots. "
            "Since the ground was dry that week, watering the sapling mattered a lot. "
            "Riya watered her tree with care every single morning before walking to school. "
            "After a whole month, tiny new leaves sprouted from the thin green branches. "
            "Riya felt proud each time she walked past her small, growing little tree. "
            "The whole class promised their teacher to keep caring for the trees together."
        ),
        difficulty_rank=22,
        takeaway="Caring for something daily, even in small ways, helps it grow strong.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What was Riya's class chosen to do?",
                ["Plant new trees", "Clean the garden", "Paint the fence", "Build a shed"],
                "Plant new trees",
                "The passage says Riya's class was chosen to plant new trees.",
            ),
            QuestionSeed(
                "literal_recall",
                "What tool did each student receive?",
                ["A wooden shovel", "A metal rake", "A watering can", "A pair of gloves"],
                "A wooden shovel",
                "The passage says each student received a sapling and a wooden shovel.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did watering the sapling matter so much that week?",
                ["Because the ground was dry", "Because it was very hot", "Because the sapling was sick", "Because rain was expected"],
                "Because the ground was dry",
                "The passage says since the ground was dry that week, watering mattered a lot.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Riya do right after digging the hole?",
                ["Placed her sapling and pressed soil around it", "Watered it every morning", "Watched leaves sprout", "Promised to care for it"],
                "Placed her sapling and pressed soil around it",
                "The passage says she placed her sapling gently and pressed soil around its roots after digging.",
            ),
            QuestionSeed(
                "literal_recall",
                "What appeared after a whole month?",
                ["Tiny new leaves", "Bright flowers", "Ripe fruit", "Tall branches"],
                "Tiny new leaves",
                "The passage says after a whole month, tiny new leaves sprouted.",
            ),
            QuestionSeed(
                "inference",
                "Why did Riya feel proud when she walked past her tree?",
                ["She helped it grow with her own care", "She wanted a prize", "She liked the shovel", "Her teacher told her to feel proud"],
                "She helped it grow with her own care",
                "Riya watered and cared for the tree herself, so watching it grow made her proud.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'sprouted' mean?",
                ["Began to grow", "Fell off the tree", "Turned brown", "Stopped growing"],
                "Began to grow",
                "'Tiny new leaves sprouted' means they began to grow.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the whole class promise?",
                ["To keep caring for the trees", "To plant more gardens", "To win a prize", "To stop watering the trees"],
                "To keep caring for the trees",
                "The passage says the whole class promised to keep caring for the trees together.",
            ),
        ],
    ),
    PassageSeed(
        title="The Fallen Tree",
        body=(
            "During the storm, strong winds knocked over an old oak tree near the road. "
            "It fell across the narrow road that led straight to Aisha's small school. "
            "Because the fallen tree blocked the road, the school bus could not pass through. "
            "Aisha's father decided to walk her to school along a quiet path instead. "
            "They passed through a small, quiet park full of wet, shining green leaves. "
            "Aisha noticed puddles showing the grey morning sky like tiny round mirrors. "
            "When they finally arrived, workers were already busy cutting the fallen tree. "
            "Aisha happily thanked her father for finding another safe way to school. "
            "That evening, the narrow road was finally cleared again for the school buses."
        ),
        difficulty_rank=23,
        takeaway="Even when something blocks our path, there is often another way forward.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What knocked over the old oak tree?",
                ["Strong winds", "A passing car", "Heavy rain", "A falling branch"],
                "Strong winds",
                "The passage says strong winds knocked over an old oak tree during the storm.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why could the school bus not pass through?",
                ["The fallen tree blocked the road", "The bus broke down", "The driver was late", "The road was flooded"],
                "The fallen tree blocked the road",
                "The passage says because the fallen tree blocked the road, the bus could not pass.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Aisha's father do after the tree blocked the road?",
                ["Walked her to school along a path", "Called the school bus", "Waited for workers to arrive", "Went back home"],
                "Walked her to school along a path",
                "The passage says her father decided to walk her to school along a quiet path instead.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Aisha notice in the puddles?",
                ["The grey morning sky", "Fallen leaves", "Her own reflection", "Small fish"],
                "The grey morning sky",
                "The passage says Aisha noticed puddles showing the grey morning sky like tiny mirrors.",
            ),
            QuestionSeed(
                "literal_recall",
                "What were workers doing when they arrived at school?",
                ["Cutting the fallen tree", "Cleaning the park", "Fixing the school bus", "Painting the road"],
                "Cutting the fallen tree",
                "The passage says workers were already busy cutting the fallen tree.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'blocked' mean?",
                ["Stopped something from passing", "Made something faster", "Cleaned something up", "Painted something bright"],
                "Stopped something from passing",
                "The fallen tree 'blocked' the road, meaning it stopped things from passing.",
            ),
            QuestionSeed(
                "inference",
                "Why was Aisha thankful to her father?",
                ["He found a safe way for her to reach school", "He fixed the school bus", "He cut down the tree", "He gave her an umbrella"],
                "He found a safe way for her to reach school",
                "Aisha thanked her father for finding another safe way to school despite the blocked road.",
            ),
            QuestionSeed(
                "literal_recall",
                "When was the road finally cleared?",
                ["That evening", "The next morning", "Two days later", "The following week"],
                "That evening",
                "The passage says that evening, the narrow road was finally cleared again.",
            ),
        ],
    ),
    PassageSeed(
        title="The River and the Village",
        body=(
            "Farmers living in the village depend on the river. "
            "They use it for growing their daily crops. "
            "One long summer, very little rain fell, and the river grew shallow and slow. "
            "Because there was much less water, many crops began to wither very quickly. "
            "The worried village elders met together to discuss what should be done next. "
            "They finally decided to dig a small canal from a nearby, deep lake. "
            "Villagers worked together for many long days to finish digging the narrow canal. "
            "Soon, fresh water flowed steadily into the thirsty, cracked fields once again. "
            "Slowly, the tired crops turned green again and began growing strong and tall. "
            "The grateful villagers had a small feast together to thank each other warmly."
        ),
        difficulty_rank=24,
        takeaway="Working together can solve problems too big for one person alone.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What do farmers in the village depend on?",
                ["The river", "A well", "A large lake", "Rain barrels"],
                "The river",
                "The passage says farmers living in the village depend on the river.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did the crops begin to wither?",
                ["There was much less water", "The soil was too rocky", "Insects ate the crops", "The farmers stopped working"],
                "There was much less water",
                "The passage says because there was much less water, many crops began to wither.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the village elders do after meeting together?",
                ["Decided to dig a canal", "Prayed for rain", "Moved to a new village", "Bought water from another town"],
                "Decided to dig a canal",
                "The passage says they finally decided to dig a small canal from a nearby lake.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where did the canal bring water from?",
                ["A nearby lake", "The ocean", "A distant river", "A rain cloud"],
                "A nearby lake",
                "The passage says they decided to dig a canal from a nearby, deep lake.",
            ),
            QuestionSeed(
                "inference",
                "Why did the villagers work together to dig the canal?",
                ["They needed water quickly to save their crops", "They wanted to build a swimming pool", "They were bored during the summer", "They were told to by outsiders"],
                "They needed water quickly to save their crops",
                "With crops withering from lack of water, working together to bring water fast was urgent.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'shallow' mean?",
                ["Not deep", "Very wide", "Extremely cold", "Full of fish"],
                "Not deep",
                "The river grew 'shallow,' meaning it was not deep, because of the lack of rain.",
            ),
            QuestionSeed(
                "literal_recall",
                "What happened after fresh water flowed into the fields?",
                ["The crops turned green again", "The river dried up completely", "The villagers moved away", "The canal collapsed"],
                "The crops turned green again",
                "The passage says slowly, the tired crops turned green again and began growing strong.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did the villagers celebrate at the end?",
                ["With a small feast", "With a parade", "With a dance festival", "With fireworks"],
                "With a small feast",
                "The passage says the grateful villagers had a small feast together to thank each other.",
            ),
        ],
    ),
    PassageSeed(
        title="The Market Helper",
        body=(
            "Every Sunday morning, Arjun went happily to the busy market with his kind mother. "
            "The market was full of colourful stalls, tasty snacks, and cheerful voices. "
            "An old vendor named Kamala sold fresh greens from a small wooden cart. "
            "One busy day, her cart wheel suddenly broke and greens rolled onto the road. "
            "Many people walked quickly past without stopping to help the worried woman. "
            "Arjun quickly ran over and carefully picked up the scattered greens. "
            "He placed each one back gently into her old wooden basket. "
            "Kamala thanked Arjun warmly and gave him a big, happy smile. "
            "She also gave him a ripe, juicy, sweet mango as a small reward. "
            "Arjun walked home feeling proud that he had helped a stranger."
        ),
        difficulty_rank=25,
        takeaway="Helping someone in need, even a stranger, is an act of kindness.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Who did Arjun go to the market with?",
                ["His mother", "His father", "His friend", "His teacher"],
                "His mother",
                "The passage says Arjun went to the market with his mother.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Kamala sell?",
                ["Fresh greens", "Ripe fruit", "Sweet snacks", "Clay pots"],
                "Fresh greens",
                "The passage says Kamala sold fresh greens.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did the greens roll onto the road?",
                [
                    "The cart wheel broke",
                    "Arjun dropped them",
                    "A dog knocked the cart",
                    "It started raining",
                ],
                "The cart wheel broke",
                "The passage says the cart wheel suddenly broke and the greens rolled onto the road.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Arjun do right after the greens fell?",
                ["He picked them up", "He bought a mango", "He went home", "He told his mother"],
                "He picked them up",
                "The passage says Arjun quickly ran over and picked up the scattered greens.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after Arjun helped Kamala?",
                ["She gave him a mango", "She scolded him", "She closed her cart", "She called his mother"],
                "She gave him a mango",
                "The passage says Kamala thanked Arjun and gave him a mango after he helped her.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'scattered' mean?",
                [
                    "Spread all over the ground",
                    "Neatly stacked in piles",
                    "Hidden inside a bag",
                    "Sold to a customer",
                ],
                "Spread all over the ground",
                "The greens rolled onto the road, so 'scattered' means spread all over the ground.",
            ),
            QuestionSeed(
                "inference",
                "How did Kamala most likely feel when Arjun helped her?",
                ["Thankful", "Angry", "Bored", "Confused"],
                "Thankful",
                "Kamala thanked Arjun warmly and smiled, showing she felt thankful.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did Arjun feel at the end of the story?",
                ["Proud", "Sad", "Scared", "Tired"],
                "Proud",
                "The passage says Arjun walked home feeling proud.",
            ),
        ],
    ),
    PassageSeed(
        title="Tom's Tower",
        body=(
            "Tom loved building tall things with his old wooden toy blocks every weekend. "
            "One rainy afternoon, he decided to build an enormous tower all by himself. "
            "He stacked block after block, checking that each one stayed perfectly balanced. "
            "Just as he placed the final block, his little brother ran quickly by. "
            "The tall tower wobbled and crashed loudly onto the hard wooden floor. "
            "Tom felt his eyes fill with tears of sadness and quiet anger. "
            "His brother said sorry and offered to help rebuild the tower together. "
            "Slowly, working side by side, the two brothers built an even taller tower. "
            "Tom realized that sharing the work made building the tower much easier and sturdier. "
            "Tom learned that asking for help is never something to feel ashamed about."
        ),
        difficulty_rank=26,
        takeaway="Working through a setback with someone else can lead to a better result.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did Tom love building with?",
                ["Wooden toy blocks", "Plastic bricks", "Paper boxes", "Sand"],
                "Wooden toy blocks",
                "The passage says Tom loved building tall things with his old wooden toy blocks.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did the tower crash to the floor?",
                ["His little brother ran by and it wobbled", "Tom knocked it over on purpose", "The blocks were too heavy", "The floor was uneven"],
                "His little brother ran by and it wobbled",
                "The passage says just as he placed the final block, his brother ran by and the tower wobbled and crashed.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did Tom feel after the tower crashed?",
                ["Sad and angry", "Happy and relieved", "Bored and sleepy", "Proud and excited"],
                "Sad and angry",
                "The passage says Tom felt his eyes fill with tears of sadness and quiet anger.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Tom's brother do after the tower crashed?",
                ["Said sorry and offered to help rebuild", "Ran away laughing", "Blamed Tom for the crash", "Left the room"],
                "Said sorry and offered to help rebuild",
                "The passage says his brother said sorry and offered to help rebuild the tower together.",
            ),
            QuestionSeed(
                "inference",
                "Why did the second tower turn out taller and sturdier?",
                ["The brothers worked together on it", "Tom used better blocks", "The brother built it alone", "They used glue this time"],
                "The brothers worked together on it",
                "The passage says working side by side, the two brothers built an even taller tower.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'sturdier' mean?",
                ["More stable and strong", "More colorful", "Much smaller", "Much taller only"],
                "More stable and strong",
                "A 'sturdier' tower is one that is more stable and strong, less likely to fall.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Tom realize about sharing the work?",
                ["It made the tower easier to build", "It made the work slower", "It was not helpful", "It made the tower smaller"],
                "It made the tower easier to build",
                "The passage says Tom realized that sharing the work made building the tower much easier.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Tom learn about asking for help?",
                ["It is nothing to feel ashamed about", "It should be avoided", "It makes you look weak", "It is only for emergencies"],
                "It is nothing to feel ashamed about",
                "The passage says Tom learned that asking for help is never something to feel ashamed about.",
            ),
        ],
    ),
    PassageSeed(
        title="The Wetland Birds",
        body=(
            "Every winter, thousands of colorful birds migrate to the warm wetlands nearby. "
            "Experts visit the wetlands each winter to carefully count and study these birds. "
            "This year, a young expert named Doctor Rao led the small research team. "
            "She noticed that far fewer birds had arrived compared to all previous years. "
            "Doctor Rao guessed that pollution near their usual resting spots had caused this drop. "
            "Her team tested the water samples and found the water was badly polluted. "
            "Local officials quickly began cleaning the wetlands carefully to fix the growing problem. "
            "Within just one year, the water became clearer and much healthier for wildlife. "
            "The following winter, even more birds happily returned to the peaceful wetlands. "
            "Everyone was relieved that the birds' favorite home was safe once more."
        ),
        difficulty_rank=27,
        takeaway="Fixing pollution can help nature heal and return to how it once was.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Where do the birds migrate to every winter?",
                ["The warm wetlands", "A cold mountain", "A dry desert", "A busy city"],
                "The warm wetlands",
                "The passage says every winter, thousands of colorful birds migrate to the warm wetlands.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who led the research team this year?",
                ["Doctor Rao", "A local farmer", "The village elder", "A school teacher"],
                "Doctor Rao",
                "The passage says a young expert named Doctor Rao led the small research team.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did fewer birds arrive that year?",
                ["Pollution near their resting spots", "A stronger storm than usual", "Too many visitors nearby", "A shortage of food"],
                "Pollution near their resting spots",
                "The passage says Doctor Rao guessed that pollution near their resting spots caused the drop.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the team do after testing the water?",
                ["Found the water was polluted", "Counted the birds", "Cleaned the wetlands themselves", "Left the wetlands"],
                "Found the water was polluted",
                "The passage says her team tested the water samples and found the water was badly polluted.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who began cleaning the wetlands?",
                ["Local officials", "Doctor Rao alone", "The birds", "School children"],
                "Local officials",
                "The passage says local officials quickly began cleaning the wetlands to fix the problem.",
            ),
            QuestionSeed(
                "inference",
                "Why did more birds return the following winter?",
                ["The water became cleaner and healthier", "The wetlands became bigger", "There was less competition for food", "The weather became warmer"],
                "The water became cleaner and healthier",
                "After cleaning, the water became clearer and healthier, which likely drew more birds back.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'relieved' mean?",
                ["Feeling less worried", "Feeling very tired", "Feeling confused", "Feeling angry"],
                "Feeling less worried",
                "Everyone felt 'relieved,' meaning less worried, once the birds' home was safe again.",
            ),
            QuestionSeed(
                "literal_recall",
                "How long did it take for the water to become healthier?",
                ["Within one year", "Within a week", "Within a month", "Within five years"],
                "Within one year",
                "The passage says within just one year, the water became clearer and much healthier.",
            ),
        ],
    ),
    PassageSeed(
        title="The Clever Crow",
        body=(
            "Nina's granny told her an old story one evening about a clever crow. "
            "Long ago, a thirsty crow found a jug with very little water inside. "
            "The crow's short beak could not reach down far enough to drink. "
            "Instead of giving up, the clever crow thought carefully of a clever plan. "
            "She began dropping small round pebbles into the jug, one by one. "
            "Slowly, the water level rose higher and higher with each dropped pebble. "
            "Finally, the water reached the top, and the happy crow drank at last. "
            "Nina asked her granny why the crow used pebbles instead of simply giving up. "
            "Her granny smiled warmly and said being clever can solve even the trickiest problems. "
            "Nina loved this old story very much indeed. "
            "She promised to remember the clever plan forever."
        ),
        difficulty_rank=28,
        takeaway="Thinking of a new approach can solve a problem that seems impossible at first.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Who told Nina the story about the crow?",
                ["Her granny", "Her teacher", "Her mother", "Her friend"],
                "Her granny",
                "The passage says Nina's granny told her an old story about a clever crow.",
            ),
            QuestionSeed(
                "literal_recall",
                "Why couldn't the crow drink the water at first?",
                ["Her beak could not reach it", "The jug was empty", "The water was dirty", "The jug was too heavy"],
                "Her beak could not reach it",
                "The passage says the crow's short beak could not reach down far enough to drink.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did the water level rise in the jug?",
                ["The crow dropped pebbles into it", "It started raining", "The crow poured in more water", "The jug tilted over"],
                "The crow dropped pebbles into it",
                "The passage says she began dropping pebbles, and the water level rose with each one.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the crow do right before the water reached the top?",
                ["Kept dropping pebbles one by one", "Flew away from the jug", "Gave up trying", "Found a different jug"],
                "Kept dropping pebbles one by one",
                "The passage says the water rose higher with each dropped pebble until it finally reached the top.",
            ),
            QuestionSeed(
                "inference",
                "What lesson does the granny's story teach?",
                ["Clever thinking can solve tricky problems", "Crows should not drink water", "Giving up is sometimes best", "Jugs are dangerous for birds"],
                "Clever thinking can solve tricky problems",
                "Her granny said being clever can solve even the trickiest problems, which is the story's lesson.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'thirsty' mean?",
                ["Needing water to drink", "Feeling very sleepy", "Feeling very hungry", "Feeling very cold"],
                "Needing water to drink",
                "A 'thirsty' crow is one that needs water to drink.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Nina promise to remember?",
                ["The clever plan", "Her granny's name", "The jug's shape", "The crow's color"],
                "The clever plan",
                "The passage says she promised to remember the clever plan forever.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did Nina feel about the story?",
                ["She loved it very much", "She found it boring", "She was confused by it", "She was scared by it"],
                "She loved it very much",
                "The passage says Nina loved this old story very much indeed.",
            ),
        ],
    ),
    PassageSeed(
        title="Republic Day",
        body=(
            "On Republic Day, the whole school gathered early for a special morning assembly. "
            "Students from every single class had practiced a patriotic dance for many weeks. "
            "Because the ground was still wet from rain, dancers worried quietly about slipping. "
            "Teachers quickly spread dry sand across the wet patches to make it safer. "
            "The principal raised the flag as everyone stood tall and saluted proudly together. "
            "Next, the dancers performed smoothly without a single slip or sudden fall. "
            "Afterward, a group of students recited a poem about freedom and great courage. "
            "Parents sitting in the audience clapped warmly for every single dance and poem. "
            "Even the youngest students felt proud to take part that day. "
            "The morning ended with everyone singing the national anthem together. "
            "The whole school felt proud of their country together on that special morning."
        ),
        difficulty_rank=29,
        takeaway="Preparing carefully for a celebration helps everyone enjoy it safely together.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Why did the school gather early?",
                ["For a special Republic Day assembly", "For a sports competition", "For a fire drill", "For a school picnic"],
                "For a special Republic Day assembly",
                "The passage says on Republic Day, the whole school gathered early for a special assembly.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why were the dancers worried about slipping?",
                ["The ground was still wet from rain", "They forgot the dance steps", "Their shoes were too big", "The music was too fast"],
                "The ground was still wet from rain",
                "The passage says because the ground was still wet from rain, dancers worried about slipping.",
            ),
            QuestionSeed(
                "sequencing",
                "What did teachers do before the dance performance?",
                ["Spread dry sand on the wet patches", "Raised the flag", "Recited a poem", "Sang the anthem"],
                "Spread dry sand on the wet patches",
                "The passage says teachers quickly spread dry sand across the wet patches to make it safer.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the students recite after the dance?",
                ["A poem about freedom and courage", "A song about rain", "A story about a crow", "A speech about sports"],
                "A poem about freedom and courage",
                "The passage says a group of students recited a poem about freedom and great courage.",
            ),
            QuestionSeed(
                "inference",
                "Why did the teachers spread sand on the ground?",
                ["To keep the dancers safe from slipping", "To make the ground look nicer", "To dry the ground faster", "To mark the dance area"],
                "To keep the dancers safe from slipping",
                "Since the dancers were worried about slipping on wet ground, spreading sand was meant to keep them safe.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'patriotic' mean?",
                ["Showing love for one's country", "Showing fear of dancing", "Showing skill in sports", "Showing interest in poems"],
                "Showing love for one's country",
                "A 'patriotic' dance is one that shows love and pride for one's country.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did the morning end?",
                ["With everyone singing the national anthem", "With a fireworks show", "With a school lunch", "With students going home early"],
                "With everyone singing the national anthem",
                "The passage says the morning ended with everyone singing the national anthem together.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did parents react to the performances?",
                ["They clapped warmly", "They stayed silent", "They left early", "They took photos only"],
                "They clapped warmly",
                "The passage says parents sitting in the audience clapped warmly for every dance and poem.",
            ),
        ],
    ),
    PassageSeed(
        title="Aunt Meena's Bakery",
        body=(
            "Every summer, Aunt Meena's small bakery gets very busy. "
            "It is busier than any other season of the year. "
            "This year, her old oven suddenly broke down. "
            "It happened just two days before a big wedding order. "
            "Because the oven was broken, she could not bake the wedding cake on time at all. "
            "Worried, Aunt Meena quickly called every repair shop in town for some quick help. "
            "Finally, a kind repairman quickly agreed to fix the oven that same night for her. "
            "He explained that a loose wire had truly caused the oven to stop heating properly. "
            "Aunt Meena stayed up baking through the night to finish the lovely cake. "
            "The next morning, she carefully delivered the lovely cake right on time. "
            "The happy customers all said it was the best wedding cake they had ever tasted."
        ),
        difficulty_rank=30,
        takeaway="Staying calm and asking for help can rescue a plan that seems ruined.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "When does Aunt Meena's bakery get very busy?",
                ["Every summer", "Every winter", "Every Monday", "Every holiday"],
                "Every summer",
                "The passage says every summer, Aunt Meena's small bakery gets very busy.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why couldn't Aunt Meena bake the wedding cake on time?",
                ["Her oven had broken down", "She ran out of flour", "She was sick that day", "The order was cancelled"],
                "Her oven had broken down",
                "The passage says because the oven was broken, she could not bake the wedding cake on time.",
            ),
            QuestionSeed(
                "literal_recall",
                "What caused the oven to stop heating?",
                ["A loose wire", "A broken door", "A cracked shelf", "A missing part"],
                "A loose wire",
                "The passage says a loose wire had caused the oven to stop heating properly.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Aunt Meena do after the repairman fixed the oven?",
                ["Stayed up baking through the night", "Called more repair shops", "Cancelled the order", "Went to sleep early"],
                "Stayed up baking through the night",
                "The passage says after the fix, Aunt Meena stayed up baking through the night to finish the cake.",
            ),
            QuestionSeed(
                "inference",
                "Why did Aunt Meena call so many repair shops?",
                ["She urgently needed the oven fixed before the deadline", "She wanted the cheapest price", "She was curious about ovens", "She wanted a new oven"],
                "She urgently needed the oven fixed before the deadline",
                "With the wedding order due in two days, she urgently needed the oven working again.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'delivered' mean?",
                ["Brought and given to someone", "Thrown away", "Left behind", "Hidden safely"],
                "Brought and given to someone",
                "She 'delivered' the cake, meaning she brought it and gave it to the customer.",
            ),
            QuestionSeed(
                "literal_recall",
                "When did she deliver the cake?",
                ["The next morning, right on time", "Two days late", "The same evening", "A week later"],
                "The next morning, right on time",
                "The passage says the next morning, she carefully delivered the lovely cake right on time.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the happy customers say about the cake?",
                ["It was the best wedding cake they had tasted", "It was too sweet", "It arrived late", "It was too small"],
                "It was the best wedding cake they had tasted",
                "The passage says the happy customers said it was the best wedding cake they had ever tasted.",
            ),
        ],
    ),
    PassageSeed(
        title="Diwali Homecoming",
        body=(
            "Every Diwali, Meena's family gathers at their family home in the village. "
            "This year, Meena's cousin Vikram was flying home from another country for the first time. "
            "Because his flight was delayed by several hours, the family waited at the airport. "
            "When Vikram walked through the gate, everyone cheered and hugged him warmly. "
            "That evening, the family lit rows of small clay lamps along the courtyard wall. "
            "Grandma cooked Vikram's favorite sweet dish, which filled the house with a warm smell. "
            "After dinner, the children lit sparklers in the garden while adults watched and chatted. "
            "Vikram said that no festival in any other country felt as warm as this one. "
            "Before sleeping, Meena thought about how lucky she felt to have her family together again. "
            "The whole family agreed that this Diwali would stay in their memories for many years."
        ),
        difficulty_rank=31,
        takeaway="A family reunion can make a festival feel more meaningful than ever before.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Where does Meena's family gather every Diwali?",
                ["Their family home in the village", "A hotel in the city", "Vikram's new house abroad", "A temple near the airport"],
                "Their family home in the village",
                "The passage says every Diwali, Meena's family gathers at their family home in the village.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did the family wait anxiously at the airport?",
                ["Vikram's flight was delayed", "The airport was closed", "They arrived too early", "Vikram missed his flight"],
                "Vikram's flight was delayed",
                "The passage says because his flight was delayed by several hours, the family waited at the airport.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the family do right after Vikram walked through the gate?",
                ["Cheered and hugged him", "Lit clay lamps", "Ate dinner", "Lit sparklers"],
                "Cheered and hugged him",
                "The passage says when Vikram walked through the gate, everyone cheered and hugged him warmly.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Grandma cook?",
                ["Vikram's favorite sweet dish", "A spicy curry", "Fried snacks", "A birthday cake"],
                "Vikram's favorite sweet dish",
                "The passage says Grandma cooked Vikram's favorite sweet dish.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the children do after dinner?",
                ["Lit sparklers in the garden", "Went to the airport", "Cooked a sweet dish", "Fell asleep"],
                "Lit sparklers in the garden",
                "The passage says after dinner, the children lit sparklers in the garden.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'delayed' mean?",
                ["Made later than planned", "Cancelled completely", "Made earlier than planned", "Moved to a new location"],
                "Made later than planned",
                "A 'delayed' flight is one that is made later than planned.",
            ),
            QuestionSeed(
                "inference",
                "Why did Vikram say no festival abroad felt as warm as this one?",
                ["Being with family made it special", "The weather was better at home", "The food was tastier here", "The lamps were brighter here"],
                "Being with family made it special",
                "Vikram had been away from family, so being reunited for Diwali made it feel especially warm.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did Meena feel lucky before falling asleep?",
                ["She had her family together again", "She got a new gift", "She won a prize", "She ate her favorite dish"],
                "She had her family together again",
                "The passage says Meena thought about how lucky she felt to have her family together again.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the whole family agree about this Diwali?",
                ["It would stay in their memories for years", "It was the best food ever", "It was too short", "It should happen every month"],
                "It would stay in their memories for years",
                "The passage says the whole family agreed that this Diwali would stay in their memories for many years.",
            ),
        ],
    ),
    PassageSeed(
        title="The Model Volcano",
        body=(
            "Our science teacher announced that our class would build a simple model volcano for the fair. "
            "Working in small teams, we mixed baking soda, vinegar, and food coloring in a plastic bottle. "
            "Before the reaction, our teacher explained why the mixture would bubble and overflow like lava. "
            "On the day of the fair, nervous students set up their models across the school hall. "
            "When Priya's team finally poured in the vinegar, red foam erupted suddenly over the model. "
            "Visiting parents gathered around, clapping and asking questions about how the eruption worked. "
            "Judges walked slowly between the tables, noting each team's reasoning and overall results. "
            "Priya's team was thrilled when their volcano won a prize for the best reasoning. "
            "Our teacher reminded everyone that learning the ideas mattered far more than winning any prize. "
            "Priya said she would remember this science fair for a long time."
        ),
        difficulty_rank=32,
        takeaway="Understanding how something works matters more than winning a prize for it.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did the class build for the science fair?",
                ["A model volcano", "A model bridge", "A robot arm", "A weather station"],
                "A model volcano",
                "The passage says the class would build a simple model volcano for the fair.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the teams mix in the bottle?",
                ["Baking soda, vinegar, and food coloring", "Sand and water", "Sugar and salt", "Paint and glue"],
                "Baking soda, vinegar, and food coloring",
                "The passage says they mixed baking soda, vinegar, and food coloring in a plastic bottle.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did the mixture bubble and overflow?",
                ["The vinegar reacted with the baking soda", "The bottle was shaken hard", "The room was too hot", "The food coloring caused it"],
                "The vinegar reacted with the baking soda",
                "The passage says the teacher explained why the mixture would bubble, referring to the vinegar and baking soda reaction.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened right after Priya's team poured in the vinegar?",
                ["Red foam erupted over the model", "Parents gathered around", "Judges walked between tables", "The prize was announced"],
                "Red foam erupted over the model",
                "The passage says when Priya's team poured in the vinegar, red foam erupted suddenly over the model.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did judges note as they walked between tables?",
                ["Each team's reasoning and results", "Each team's costumes", "The color of each volcano", "How loud each team was"],
                "Each team's reasoning and results",
                "The passage says judges walked between the tables, noting each team's reasoning and overall results.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'reasoning' mean?",
                ["The thinking behind an explanation", "The color of the model", "The size of the bottle", "The name of the team"],
                "The thinking behind an explanation",
                "'Reasoning' refers to the thinking a team used to explain their science project.",
            ),
            QuestionSeed(
                "inference",
                "Why did the teacher say learning mattered more than winning?",
                ["Understanding the science is the real goal", "Prizes are not important at all", "The volcano did not work well", "Priya's team should have won more"],
                "Understanding the science is the real goal",
                "The teacher's reminder suggests that truly understanding the science matters more than the prize itself.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why was Priya's team thrilled?",
                ["They won a prize for the best reasoning", "They finished first", "They had the biggest volcano", "They used the most vinegar"],
                "They won a prize for the best reasoning",
                "The passage says Priya's team was thrilled when their volcano won a prize for the best reasoning.",
            ),
            QuestionSeed(
                "literal_recall",
                "How did Priya feel about the science fair?",
                ["She would remember it for a long time", "She wanted to forget it", "She thought it was boring", "She was disappointed"],
                "She would remember it for a long time",
                "The passage says Priya said she would remember this science fair for a long time.",
            ),
        ],
    ),
    PassageSeed(
        title="Mister Iyer's Puppy",
        body=(
            "Every Saturday morning, elderly Mister Iyer feeds the stray dogs living near the train station. "
            "One cold morning, he noticed a thin, shivering puppy hiding quietly beneath a wooden bench. "
            "Because the puppy looked sick and weak, Mister Iyer decided to take it home right away. "
            "He wrapped the shivering puppy gently in his warm woolen scarf before starting the walk. "
            "At home, his wife prepared warm milk while Mister Iyer checked the puppy for any injuries. "
            "Over the following days, the puppy slowly grew stronger, playful, and more relaxed around people. "
            "Mister Iyer's grandkids visited often, delighted to play with their new furry family member. "
            "Eventually, the puppy became a cheerful little companion for the entire Iyer family. "
            "Mister Iyer often said that small acts of kindness can change another creature's whole life. "
            "The puppy grew up to greet every visitor at the door with a wagging tail."
        ),
        difficulty_rank=33,
        takeaway="Small acts of kindness toward animals can change their whole lives.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Who does Mister Iyer feed every Saturday morning?",
                ["Stray dogs near the train station", "Birds in the park", "Cats in his yard", "Fish in a pond"],
                "Stray dogs near the train station",
                "The passage says every Saturday morning, Mister Iyer feeds the stray dogs near the train station.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where was the puppy hiding?",
                ["Beneath a wooden bench", "Behind a trash can", "Inside a box", "Under a car"],
                "Beneath a wooden bench",
                "The passage says he noticed a puppy hiding quietly beneath a wooden bench.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did Mister Iyer decide to take the puppy home?",
                ["It looked sick and weak", "It was following him", "It was raining heavily", "His grandkids asked him to"],
                "It looked sick and weak",
                "The passage says because the puppy looked sick and weak, Mister Iyer decided to take it home right away.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Mister Iyer do before starting the walk home?",
                ["Wrapped the puppy in his scarf", "Gave it warm milk", "Checked it for injuries", "Called his wife"],
                "Wrapped the puppy in his scarf",
                "The passage says he wrapped the shivering puppy gently in his warm woolen scarf before starting the walk.",
            ),
            QuestionSeed(
                "sequencing",
                "What did his wife do when they got home?",
                ["Prepared warm milk", "Wrapped the puppy in a scarf", "Went to the train station", "Played with the grandkids"],
                "Prepared warm milk",
                "The passage says at home, his wife prepared warm milk while Mister Iyer checked the puppy.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'shivering' mean?",
                ["Shaking from cold or fear", "Sleeping deeply", "Running quickly", "Barking loudly"],
                "Shaking from cold or fear",
                "A 'shivering' puppy is one shaking, usually from being cold or scared.",
            ),
            QuestionSeed(
                "inference",
                "Why did the puppy become more playful over the following days?",
                ["It was getting healthier and felt safe", "It missed the train station", "It wanted to go outside more", "It was scared of the grandkids"],
                "It was getting healthier and felt safe",
                "As the puppy recovered and was cared for, it naturally grew stronger and more comfortable.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who visited often to play with the puppy?",
                ["Mister Iyer's grandkids", "The neighbors' children", "Mister Iyer's coworkers", "Strangers from the station"],
                "Mister Iyer's grandkids",
                "The passage says Mister Iyer's grandkids visited often, delighted to play with their new furry family member.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Mister Iyer often say about kindness?",
                ["It can change another creature's whole life", "It is only for pets", "It should be saved for family", "It rarely makes a difference"],
                "It can change another creature's whole life",
                "The passage says Mister Iyer often said that small acts of kindness can change another creature's whole life.",
            ),
        ],
    ),
    PassageSeed(
        title="The Village and the Flood",
        body=(
            "During monsoon season, heavy rain often causes the small river near Devi's village to overflow. "
            "This year, the rising water level worried villagers more than it typically had in previous years. "
            "Because their homes stood very close to the riverbank, several families feared sudden and serious flooding. "
            "Local officials arrived. They warned everyone to move their belongings to higher ground before nightfall. "
            "Devi's family packed important documents, warm blankets, and enough food for several uncertain days ahead. "
            "That night, the exhausted village gathered together safely inside the sturdy community hall on the hill. "
            "By morning, the rain had finally stopped, though the swollen river remained very high and fast. "
            "Slowly, over the following week, the water receded, revealing muddy but thankfully undamaged homes below. "
            "Devi realized that quick thinking and community teamwork had kept every single family safe. "
            "She hoped the village would remember this lesson before the next monsoon season arrived."
        ),
        difficulty_rank=34,
        takeaway="Quick thinking and working together as a community can prevent disaster.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What does heavy monsoon rain often cause near Devi's village?",
                ["The small river to overflow", "The wells to dry up", "The roads to crack", "The crops to burn"],
                "The small river to overflow",
                "The passage says heavy rain often causes the small river near Devi's village to overflow.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did several families fear flooding this year?",
                ["Their homes stood close to the riverbank", "The village had no warning system", "The rain lasted only one hour", "The river was completely dry"],
                "Their homes stood close to the riverbank",
                "The passage says because their homes stood very close to the riverbank, several families feared flooding.",
            ),
            QuestionSeed(
                "sequencing",
                "What did local officials do after arriving?",
                ["Warned everyone to move belongings to higher ground", "Repaired the riverbank", "Closed the community hall", "Left the village"],
                "Warned everyone to move belongings to higher ground",
                "The passage says local officials arrived and warned everyone to move their belongings to higher ground.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Devi's family pack?",
                ["Documents, blankets, and food", "Furniture and toys", "Farm tools", "Books and clothes only"],
                "Documents, blankets, and food",
                "The passage says Devi's family packed important documents, warm blankets, and enough food.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where did the village gather that night?",
                ["The sturdy community hall on the hill", "Their own homes", "The riverbank", "The school building"],
                "The sturdy community hall on the hill",
                "The passage says that night, the exhausted village gathered together safely inside the sturdy community hall.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'receded' mean?",
                ["Moved back or went down", "Rose higher and higher", "Turned a different color", "Became warmer"],
                "Moved back or went down",
                "The water 'receded,' meaning it moved back and went down after the flood.",
            ),
            QuestionSeed(
                "inference",
                "Why were the revealed homes described as thankfully undamaged?",
                ["The community's quick action protected them", "The flood never actually happened", "The homes were rebuilt overnight", "The river changed its path"],
                "The community's quick action protected them",
                "Because the village acted quickly and moved to safety, their homes were spared serious damage.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did the village manage to stay safe overall?",
                ["Quick thinking and community teamwork", "Sheer luck alone", "A dam built years ago", "Help from a nearby city"],
                "Quick thinking and community teamwork",
                "The passage says Devi realized that quick thinking and community teamwork had kept every family safe.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Devi hope the village would remember?",
                ["This lesson before the next monsoon", "The names of the officials", "The cost of the flood", "The date of the flood"],
                "This lesson before the next monsoon",
                "The passage says she hoped the village would remember this lesson before the next monsoon season arrived.",
            ),
        ],
    ),
    PassageSeed(
        title="Arav's Kindness",
        body=(
            "For weeks, Arav had saved every rupee of his pocket money for a cricket bat. "
            "One afternoon, he finally had enough money and rushed to the sports store downtown. "
            "Because the store was having a sale, Arav found a better bat than expected. "
            "At the counter, he noticed an old man counting coins carefully, short of the price. "
            "Without hesitating, Arav added some of his saved money to help the stranger. "
            "The grateful man thanked him warmly, explaining the bat was a gift for his grandson. "
            "Arav walked home without buying his own bat, yet somehow he felt strangely happy. "
            "When his father heard the story that evening, he proudly bought Arav a nicer bat. "
            "Arav learned that kindness toward strangers often returns to us in unexpected ways. "
            "He never forgot the man's grateful smile at the store counter that day. "
            "From then on, Arav always kept a little extra money aside just in case."
        ),
        difficulty_rank=35,
        takeaway="A kind act, even without expecting anything back, can bring its own reward.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What was Arav saving his pocket money for?",
                ["A cricket bat", "A bicycle", "A video game", "A new phone"],
                "A cricket bat",
                "The passage says Arav had saved every rupee of his pocket money for a cricket bat.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Arav notice about the old man at the counter?",
                ["He was short of the price", "He was buying a bicycle", "He worked at the store", "He was Arav's neighbor"],
                "He was short of the price",
                "The passage says he noticed an old man counting coins carefully, short of the price.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did Arav add his own money to help?",
                ["The old man needed more to pay", "The store demanded it", "His father told him to", "He wanted a discount"],
                "The old man needed more to pay",
                "The passage says without hesitating, Arav added some of his saved money to help the stranger.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the old man do after Arav helped him?",
                ["Thanked him and explained about the gift", "Left without a word", "Asked for more money", "Called Arav's father"],
                "Thanked him and explained about the gift",
                "The passage says the grateful man thanked him warmly, explaining the bat was a gift for his grandson.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after Arav's father heard the story?",
                ["He bought Arav a nicer bat", "He returned the old bat", "He scolded Arav", "He visited the old man"],
                "He bought Arav a nicer bat",
                "The passage says when his father heard the story, he proudly bought Arav a nicer bat.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'hesitating' mean?",
                ["Pausing before deciding", "Running very fast", "Laughing loudly", "Counting money"],
                "Pausing before deciding",
                "'Without hesitating' means without pausing to decide.",
            ),
            QuestionSeed(
                "inference",
                "Why did Arav feel strangely happy despite not buying his own bat?",
                ["Helping someone felt more rewarding", "He forgot he wanted a bat", "He did not really want a bat", "He got a refund"],
                "Helping someone felt more rewarding",
                "Even without his own bat, Arav's act of kindness brought him a deeper sense of happiness.",
            ),
            QuestionSeed(
                "literal_recall",
                "What lesson did Arav learn?",
                ["Kindness often returns in unexpected ways", "Money should always be saved", "Strangers cannot be trusted", "Bats are too expensive"],
                "Kindness often returns in unexpected ways",
                "The passage says Arav learned that kindness toward strangers often returns to us in unexpected ways.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Arav start doing after that day?",
                ["Kept a little extra money aside", "Stopped saving money", "Avoided the sports store", "Gave away all his money"],
                "Kept a little extra money aside",
                "The passage says from then on, Arav always kept a little extra money aside just in case.",
            ),
        ],
    ),
    PassageSeed(
        title="The Lantern Festival",
        body=(
            "Every year, our small town holds a lantern festival beside the wide, slow-moving river. "
            "This year, strong winds threatened to blow out the hundreds of paper lanterns before dusk. "
            "Because organizers worried the festival might be cancelled, volunteers scrambled to find a clever solution. "
            "Someone suggested building simple wooden wind-breaks along the riverbank to shield the paper lanterns. "
            "Dozens of volunteers worked together, hammering boards and testing each wind-break before evening arrived. "
            "As darkness fell, families gathered along the riverbank, lanterns glowing warmly despite the gusty weather. "
            "One by one, glowing lanterns drifted down the dark river, reflecting golden light on the water. "
            "Children cheered loudly whenever a lantern survived the wind and floated out of sight. "
            "That night, our mayor thanked the volunteers for saving a tradition the whole town treasured. "
            "Everyone agreed the festival felt more special because of the challenge they had overcome. "
            "Families walked home slowly, still talking about the beautiful glowing lanterns."
        ),
        difficulty_rank=36,
        takeaway="Overcoming a challenge together can make a celebration feel even more meaningful.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What festival does the town hold every year?",
                ["A lantern festival", "A kite festival", "A harvest festival", "A boat race"],
                "A lantern festival",
                "The passage says every year, the town holds a lantern festival beside the river.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did organizers worry the festival might be cancelled?",
                ["Strong winds threatened to blow out the lanterns", "There were too few volunteers", "The river was too shallow", "It started raining heavily"],
                "Strong winds threatened to blow out the lanterns",
                "The passage says strong winds threatened to blow out the paper lanterns before dusk.",
            ),
            QuestionSeed(
                "sequencing",
                "What did volunteers do after someone suggested wind-breaks?",
                ["Hammered boards and tested each one", "Cancelled the festival", "Lit the lanterns early", "Went home"],
                "Hammered boards and tested each one",
                "The passage says dozens of volunteers worked together, hammering boards and testing each wind-break.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where did families gather as darkness fell?",
                ["Along the riverbank", "Inside the town hall", "At the school", "In the market"],
                "Along the riverbank",
                "The passage says as darkness fell, families gathered along the riverbank.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the glowing lanterns do on the river?",
                ["Drifted down, reflecting golden light", "Sank quickly", "Caught fire", "Floated upstream"],
                "Drifted down, reflecting golden light",
                "The passage says lanterns drifted down the dark river, reflecting golden light on the water.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'treasured' mean?",
                ["Valued deeply", "Ignored completely", "Forgotten quickly", "Sold for money"],
                "Valued deeply",
                "A 'treasured' tradition is one that is valued deeply by the town.",
            ),
            QuestionSeed(
                "inference",
                "Why did the festival feel more special that year?",
                ["The town overcame a real challenge together", "It lasted longer than usual", "More lanterns were used", "The weather was perfect"],
                "The town overcame a real challenge together",
                "The passage says everyone agreed the festival felt more special because of the challenge they had overcome.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did children cheer when a lantern survived the wind?",
                ["They were happy it stayed lit despite the wind", "They wanted to race it", "They thought it was funny", "They were told to cheer"],
                "They were happy it stayed lit despite the wind",
                "Given the earlier worry about wind, a surviving lantern was a small victory worth cheering for.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who did the mayor thank that night?",
                ["The volunteers", "The dancers", "The judges", "The fishermen"],
                "The volunteers",
                "The passage says that night, the mayor thanked the volunteers for saving the tradition.",
            ),
        ],
    ),
    PassageSeed(
        title="Naina's Big Night",
        body=(
            "Ever since she was small, Naina had dreamed of performing on the school's big stage. "
            "This year, she finally auditioned nervously for the lead role in the spring musical. "
            "Because so many talented students auditioned, Naina worried quietly that she stood little chance. "
            "Two days later, her drama teacher announced proudly that Naina had earned the lead role. "
            "Rehearsals proved far more demanding than Naina had imagined, lasting many long hours after school. "
            "Some evenings, tired and unhappy, she considered quietly giving up the difficult role. "
            "Her older sister reminded her gently that every skill requires patience, practice, and effort. "
            "On opening night, Naina stepped bravely onto the stage, and the packed auditorium fell silent. "
            "When the curtain closed, thunderous applause confirmed that all her hard work had paid off. "
            "Naina bowed with a wide smile, proud that she had never given up on her dream. "
            "Afterward, her sister hugged her tightly and said she had never felt prouder of anyone."
        ),
        difficulty_rank=37,
        takeaway="Patience and practice can turn a difficult challenge into a proud achievement.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What had Naina always dreamed of doing?",
                ["Performing on the school's big stage", "Winning a sports trophy", "Becoming a teacher", "Traveling abroad"],
                "Performing on the school's big stage",
                "The passage says Naina had dreamed of performing on the school's big stage.",
            ),
            QuestionSeed(
                "literal_recall",
                "What role did Naina audition for?",
                ["The lead role in the spring musical", "A background dancer", "The narrator", "A stagehand"],
                "The lead role in the spring musical",
                "The passage says she auditioned nervously for the lead role in the spring musical.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did Naina worry she had little chance?",
                ["So many talented students auditioned", "She forgot her lines", "She arrived late", "The teacher disliked her"],
                "So many talented students auditioned",
                "The passage says because so many talented students auditioned, Naina worried she stood little chance.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened two days after the audition?",
                ["The teacher announced Naina had earned the role", "Rehearsals began immediately", "The curtain opened", "Naina gave up"],
                "The teacher announced Naina had earned the role",
                "The passage says two days later, her drama teacher announced that Naina had earned the lead role.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Naina consider doing during difficult evenings?",
                ["Quietly giving up the role", "Asking for a smaller part", "Skipping rehearsals", "Talking to the teacher"],
                "Quietly giving up the role",
                "The passage says some evenings, tired and unhappy, she considered quietly giving up the difficult role.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'demanding' mean?",
                ["Requiring a lot of effort", "Very easy and simple", "Fun and relaxing", "Short and quick"],
                "Requiring a lot of effort",
                "Rehearsals being 'demanding' means they required a lot of effort and time.",
            ),
            QuestionSeed(
                "inference",
                "Why did Naina's sister remind her about patience and practice?",
                ["To encourage her not to give up", "To make her feel guilty", "To end the conversation", "To criticize her acting"],
                "To encourage her not to give up",
                "Her sister's reminder was meant to support Naina through her doubts and encourage her to keep going.",
            ),
            QuestionSeed(
                "literal_recall",
                "What happened when the curtain closed?",
                ["Thunderous applause confirmed her hard work paid off", "The audience left quietly", "Naina forgot her lines", "The teacher was disappointed"],
                "Thunderous applause confirmed her hard work paid off",
                "The passage says when the curtain closed, thunderous applause confirmed that all her hard work had paid off.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Naina's sister say after the show?",
                ["She had never felt prouder of anyone", "She wanted a role too", "She was tired of watching", "She forgot to bring flowers"],
                "She had never felt prouder of anyone",
                "The passage says her sister hugged her tightly and said she had never felt prouder of anyone.",
            ),
        ],
    ),
    PassageSeed(
        title="The Elephant and the Stream",
        body=(
            "Deep within the quiet forest, a small stream had flowed steadily past the same mossy rocks for many years. "
            "One dry summer, the stream slowly began shrinking, worrying the animals who depended on it daily. "
            "A wise old elephant noticed thirsty birds and rabbits nearby. "
            "They were gathering anxiously near the shrinking, very muddy water. "
            "Recalling an old hidden spring nearby, the elephant began digging patiently with her powerful front feet. "
            "After working for nearly an hour, cool, clear water finally began bubbling up through the ground. "
            "Grateful animals soon gathered around the small new spring, drinking freely for the first time. "
            "A clever fox suggested digging a shallow channel to guide the fresh water toward the stream. "
            "Together, the forest animals dug happily, and slowly the stream began flowing once again. "
            "Every forest creature remembered how one elephant's hard work had saved them all. "
            "The young fox often told the story to newer animals who joined the forest each spring."
        ),
        difficulty_rank=38,
        takeaway="One individual's determination can help an entire community through a crisis.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What had flowed past the mossy rocks for years?",
                ["A small stream", "A wide river", "A waterfall", "A lake"],
                "A small stream",
                "The passage says a small stream had flowed steadily past the same mossy rocks for many years.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did the stream begin shrinking?",
                ["It was a dry summer", "Animals drank too much", "The rocks blocked it", "A storm changed its path"],
                "It was a dry summer",
                "The passage says one dry summer, the stream slowly began shrinking.",
            ),
            QuestionSeed(
                "literal_recall",
                "Which animal noticed the birds and rabbits gathering anxiously?",
                ["An old elephant", "A young fox", "A tired lion", "A wise owl"],
                "An old elephant",
                "The passage says a wise old elephant noticed thirsty birds and rabbits nearby.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the elephant do after remembering the hidden spring?",
                ["Began digging with her front feet", "Called the other animals", "Drank from the stream", "Left the forest"],
                "Began digging with her front feet",
                "The passage says recalling the hidden spring, the elephant began digging patiently with her powerful front feet.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the fox suggest after animals gathered at the new spring?",
                ["Digging a channel to guide water to the stream", "Digging a second spring", "Filling in the old stream", "Moving to a new forest"],
                "Digging a channel to guide water to the stream",
                "The passage says a clever fox suggested digging a shallow channel to guide the fresh water toward the stream.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'shrinking' mean?",
                ["Becoming smaller", "Becoming louder", "Becoming cleaner", "Becoming faster"],
                "Becoming smaller",
                "A 'shrinking' stream is one that is becoming smaller.",
            ),
            QuestionSeed(
                "inference",
                "Why did the animals work together to dig the channel?",
                ["They wanted to keep the stream flowing for everyone", "They were bored during the dry summer", "The elephant ordered them to", "They wanted a bigger spring"],
                "They wanted to keep the stream flowing for everyone",
                "Since the stream mattered to all the animals, working together to guide water to it helped everyone.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did every forest creature remember about the elephant?",
                ["Her hard work had saved them all", "Her size was the biggest", "Her color was grey", "Her age was very old"],
                "Her hard work had saved them all",
                "The passage says every forest creature remembered how one elephant's hard work had saved them all.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who told the story to new animals each spring?",
                ["The young fox", "The old elephant", "A bird", "A rabbit"],
                "The young fox",
                "The passage says the young fox often told the story to newer animals who joined the forest each spring.",
            ),
        ],
    ),
    PassageSeed(
        title="The Broken Heating System",
        body=(
            "It was the coldest morning of winter. "
            "The school's old heating system suddenly stopped working entirely. "
            "Because repairs would take several days, the principal announced classes would move for now to the gym. "
            "Students grumbled about the unfamiliar setup, missing their usual desks and cozy, familiar classrooms. "
            "Teachers organized portable heaters, borrowed extra blankets, and rearranged furniture to make everyone comfy. "
            "Oddly, students soon discovered that sharing one large space led to new friends across different grade levels. "
            "Older students began helping younger ones with tricky homework during the shared study periods. "
            "By the third day, repair workers finally announced the heating system was completely fixed. "
            "Although everyone happily returned to their normal classrooms, many secretly missed the gym's cheerful, busy mood. "
            "The principal later admitted that the temporary trouble had suddenly brought the whole school closer together. "
            "Some students even asked if the whole school could share one big room again next winter. "
            "The principal laughed and promised to think about it before the following year."
        ),
        difficulty_rank=39,
        takeaway="An inconvenient problem can sometimes bring unexpected benefits.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What stopped working on the coldest morning of winter?",
                ["The school's heating system", "The school bus", "The water supply", "The electricity"],
                "The school's heating system",
                "The passage says the school's old heating system suddenly stopped working entirely.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did classes move to the gym?",
                ["Repairs would take several days", "The classrooms were being painted", "There was a fire drill", "The gym was warmer"],
                "Repairs would take several days",
                "The passage says because repairs would take several days, classes would move for now to the gym.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did teachers do to make everyone comfortable?",
                ["Organized heaters and blankets", "Cancelled classes", "Sent students home", "Opened the windows"],
                "Organized heaters and blankets",
                "The passage says teachers organized portable heaters, borrowed extra blankets, and rearranged furniture.",
            ),
            QuestionSeed(
                "sequencing",
                "What did older students do during the shared study periods?",
                ["Helped younger ones with homework", "Played games alone", "Left the gym early", "Complained to the principal"],
                "Helped younger ones with homework",
                "The passage says older students began helping younger ones with tricky homework during the shared study periods.",
            ),
            QuestionSeed(
                "inference",
                "Why did sharing one large space lead to new friendships?",
                ["Students from different grades spent time together", "The gym had more toys", "Teachers assigned new friends", "The heating made everyone happier"],
                "Students from different grades spent time together",
                "Being in one shared space naturally brought students from different grade levels into contact with each other.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'unfamiliar' mean?",
                ["Not known or new", "Very comfortable", "Extremely cold", "Well organized"],
                "Not known or new",
                "An 'unfamiliar' setup is one that is new and not previously known.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened on the third day?",
                ["Repair workers announced the heating was fixed", "Classes moved to the gym", "The principal made an announcement", "Students went home early"],
                "Repair workers announced the heating was fixed",
                "The passage says by the third day, repair workers finally announced the heating system was completely fixed.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did many students secretly miss the gym after returning to classrooms?",
                ["They had enjoyed its cheerful, busy mood", "The classrooms were too quiet", "The gym had better seats", "They disliked their teachers"],
                "They had enjoyed its cheerful, busy mood",
                "The passage says many secretly missed the gym's cheerful, busy mood after returning to their normal classrooms.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the principal admit about the whole experience?",
                ["It had brought the whole school closer together", "It was a waste of time", "It cost too much money", "It should never happen again"],
                "It had brought the whole school closer together",
                "The passage says the principal admitted that the temporary trouble had brought the whole school closer together.",
            ),
        ],
    ),
    PassageSeed(
        title="The Lighthouse Keeper",
        body=(
            "Deep in the mountains, an old lighthouse keeper named Rustom had guided ships for years. "
            "One stormy night, thick fog rolled in densely. "
            "Rustom's powerful light barely pierced through it. "
            "Worried that passing ships might not see the warning light, Rustom grew more and more anxious. "
            "Recalling stories from his grandpa, he decided to ring the old, rusted fog bell nonstop. "
            "Hour after hour, Rustom rang the bell, his tired arms aching from the effort. "
            "Just before dawn, a fishing boat radioed that the bell's steady sound had guided them home. "
            "Exhausted but relieved, Rustom finally rested, knowing his effort had likely saved several fishermen that night. "
            "The grateful fishermen later visited, bringing fresh fish and thanking the tired old keeper. "
            "From that stormy night on, Rustom never once doubted that his quiet, lonely work truly mattered. "
            "He kept the old bell polished and ready for the next foggy night at sea. "
            "Years later, sailors still spoke of the keeper whose bell had guided them through the storm."
        ),
        difficulty_rank=40,
        takeaway="Quiet, steady work can matter more than the person doing it ever realizes.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What had Rustom done for years?",
                ["Guided ships as a lighthouse keeper", "Fished for a living", "Repaired boats", "Sailed around the world"],
                "Guided ships as a lighthouse keeper",
                "The passage says an old lighthouse keeper named Rustom had guided ships for years.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did Rustom grow anxious that stormy night?",
                ["Fog made his light hard to see", "His bell was broken", "Ships were too far away", "He was very tired"],
                "Fog made his light hard to see",
                "The passage says worried that passing ships might not see the warning light, Rustom grew more and more anxious.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Rustom do after remembering his grandpa's stories?",
                ["Decided to ring the fog bell", "Turned off the light", "Went to sleep", "Called for help"],
                "Decided to ring the fog bell",
                "The passage says recalling stories from his grandpa, he decided to ring the old, rusted fog bell nonstop.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the fishing boat radio in?",
                ["The bell's sound had guided them home", "They were lost at sea", "They needed fuel", "They saw the lighthouse light"],
                "The bell's sound had guided them home",
                "The passage says a fishing boat radioed that the bell's steady sound had guided them home.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the fishermen do after they arrived safely?",
                ["Visited Rustom with fresh fish", "Called for a repair crew", "Sailed away immediately", "Reported the storm"],
                "Visited Rustom with fresh fish",
                "The passage says the grateful fishermen later visited, bringing fresh fish and thanking the tired old keeper.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'pierced' mean?",
                ["Cut through something", "Bounced off something", "Faded away slowly", "Grew brighter suddenly"],
                "Cut through something",
                "The light 'pierced' through the fog, meaning it cut through it, though only barely.",
            ),
            QuestionSeed(
                "inference",
                "Why did Rustom never doubt that his work mattered after that night?",
                ["He knew his bell had likely saved lives", "He received an award", "He got a new lighthouse", "He stopped feeling lonely"],
                "He knew his bell had likely saved lives",
                "Knowing his effort had helped save the fishermen gave Rustom lasting confidence that his work truly mattered.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Rustom keep ready for future foggy nights?",
                ["The old bell, polished", "A new lighthouse light", "Extra fishing nets", "A weather radio"],
                "The old bell, polished",
                "The passage says he kept the old bell polished and ready for the next foggy night at sea.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did sailors say about Rustom years later?",
                ["They spoke of the keeper whose bell guided them safely", "They forgot about him", "They complained about the bell's noise", "They said he retired too early"],
                "They spoke of the keeper whose bell guided them safely",
                "The passage says years later, sailors still spoke of the keeper whose bell had guided them through the storm.",
            ),
        ],
    ),
    PassageSeed(
        title="Ramesh's Tea Stall",
        body=(
            "In every corner of India, small tea stalls have quietly served travelers and neighbors for generations. "
            "Ramesh had run his tiny stall near the bus stand for almost thirty years. "
            "He never once took a break in all that time. "
            "He knew most regular customers by name, remembering exactly how sweet each person liked their tea. "
            "When a new highway opened nearby, fewer buses stopped, and business slowly grew quiet. "
            "Ramesh worried that his stall could not survive without the crowd it once depended on. "
            "His daughter, studying business in the city, suggested he sell tea near the new highway instead. "
            "At first, Ramesh doubted whether customers would find a stall in such an unfamiliar location. "
            "Slowly, curious truck drivers and other travelers began stopping, drawn in by the rich smell of freshly brewed tea. "
            "Within just a few months, Ramesh's new stall became busier and livelier than the old one ever was. "
            "Ramesh often told his daughter that adapting to change had saved the family business they both loved."
        ),
        difficulty_rank=41,
        takeaway="Being willing to adapt to change can help something old find new life.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "How long had Ramesh run his tea stall?",
                ["Almost thirty years", "Five years", "Ten years", "Fifty years"],
                "Almost thirty years",
                "The passage says Ramesh had run his tiny stall for almost thirty years.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did business at Ramesh's old stall grow quiet?",
                ["A new highway opened and fewer buses stopped", "Ramesh raised his prices", "The stall was too small", "Customers stopped liking tea"],
                "A new highway opened and fewer buses stopped",
                "The passage says when a new highway opened nearby, fewer buses stopped, and business slowly grew quiet.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who suggested Ramesh sell tea near the new highway?",
                ["His daughter", "His wife", "A customer", "A truck driver"],
                "His daughter",
                "The passage says his daughter suggested he sell tea near the new highway instead.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Ramesh do despite his doubts about the new location?",
                ["He moved his stall there anyway", "He closed his business", "He asked his customers", "He built a new highway"],
                "He moved his stall there anyway",
                "Despite his doubts, the passage shows Ramesh went on to open near the highway, where travelers slowly began stopping.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did truck drivers begin stopping at the new stall?",
                ["They were drawn by the smell of tea", "They needed directions", "They wanted to rest only", "They knew Ramesh personally"],
                "They were drawn by the smell of tea",
                "The passage says truck drivers began stopping, drawn in by the rich smell of freshly brewed tea.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'livelier' mean?",
                ["More full of energy and activity", "More quiet and calm", "More expensive", "More far away"],
                "More full of energy and activity",
                "A 'livelier' stall is one that is busier and more full of energy.",
            ),
            QuestionSeed(
                "inference",
                "Why did Ramesh doubt the new location at first?",
                ["He worried customers wouldn't recognize his stall there", "He disliked the highway", "He preferred the old bus stand's food", "He thought tea wouldn't sell there"],
                "He worried customers wouldn't recognize his stall there",
                "The passage says at first, Ramesh doubted whether customers would find a stall in such an unfamiliar location.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                ["A tea seller adapting his business to change", "A daughter studying in the city", "The history of Indian tea stalls", "A new highway construction project"],
                "A tea seller adapting his business to change",
                "The whole passage follows how Ramesh adjusted his tea stall's location to survive and thrive.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                ["To show how adapting to change can lead to success", "To warn readers about highways", "To describe how tea is made", "To compare old and new buses"],
                "To show how adapting to change can lead to success",
                "The passage's ending message about adapting to change reveals the author's purpose.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about Ramesh's daughter?",
                ["She gave her father good business advice", "She dislikes her father's work", "She wanted to take over the stall", "She moved away permanently"],
                "She gave her father good business advice",
                "Her suggestion to move near the highway ultimately saved the family business, showing she gave sound advice.",
            ),
        ],
    ),
    PassageSeed(
        title="Kavya and the Cranes",
        body=(
            "Every February, migratory cranes travel thousands of kilometers to rest briefly at a quiet wetland near Kavya's town. "
            "This year, Kavya's science class visited the wetland to observe the cranes as part of a special project. "
            "Their teacher explained that cranes rely on wetlands like this one to rest and refuel during their long journey. "
            "Kavya noticed that several birds seemed to be searching anxiously near the shore. "
            "They seemed unable to find enough food there. "
            "Their teacher explained that unusually low rainfall that year had shrunk the wetland's shallow feeding pools a great deal. "
            "Concerned, the students asked what could possibly be done to help the tired, hungry birds survive the season. "
            "Their teacher suggested writing letters to local officials, asking them to protect and restore the shrinking wetland. "
            "Excited by the idea, the whole class spent the next week drafting careful letters together. "
            "Weeks later, officials announced a plan to dig deeper channels and protect the wetland's water. "
            "Kavya felt proud knowing that her class's simple idea had helped protect a fragile habitat."
        ),
        difficulty_rank=42,
        takeaway="Young people working together can help protect something fragile and important.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Why do cranes travel to the wetland every February?",
                ["To rest during their long journey", "To build permanent nests", "To find new mates only", "To escape predators"],
                "To rest during their long journey",
                "The passage says cranes rely on the wetland to rest and refuel during their long journey.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why had the wetland's feeding pools shrunk?",
                ["Unusually low rainfall that year", "Too many visiting students", "A new dam upstream", "Pollution from factories"],
                "Unusually low rainfall that year",
                "The passage says unusually low rainfall that year had shrunk the wetland's shallow feeding pools.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Kavya notice about several birds?",
                ["They seemed unable to find enough food", "They were flying away", "They were fighting each other", "They were building nests"],
                "They seemed unable to find enough food",
                "The passage says Kavya noticed several birds seemed to be searching anxiously, unable to find enough food.",
            ),
            QuestionSeed(
                "sequencing",
                "What did the teacher suggest after students asked how to help?",
                ["Writing letters to local officials", "Visiting the wetland again", "Building a new pond", "Feeding the birds directly"],
                "Writing letters to local officials",
                "The passage says their teacher suggested writing letters to local officials to protect the wetland.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after the class sent their letters?",
                ["Officials announced a plan to help the wetland", "The cranes left immediately", "The wetland dried up completely", "The class visited a new wetland"],
                "Officials announced a plan to help the wetland",
                "The passage says weeks later, officials announced a plan to dig deeper channels and protect the wetland's water.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'refuel' mean?",
                ["Take in energy or food again", "Fly at a higher speed", "Build a new nest", "Change direction suddenly"],
                "Take in energy or food again",
                "Birds 'refuel' at a wetland by resting and eating to regain energy for their journey.",
            ),
            QuestionSeed(
                "inference",
                "Why did the teacher bring the class to the wetland?",
                ["To help them learn through direct observation", "To give them a break from class", "To test their science knowledge", "To collect crane feathers"],
                "To help them learn through direct observation",
                "Visiting the wetland allowed students to observe cranes and their struggles firsthand, deepening their understanding.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                ["Students helping protect a wetland for migrating birds", "The science of bird migration", "A class trip to a museum", "How to write a petition"],
                "Students helping protect a wetland for migrating birds",
                "The passage follows Kavya's class from observing the cranes' struggle to successfully helping protect their habitat.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                ["To show that young people can help solve real problems", "To describe crane migration patterns in detail", "To criticize local officials", "To explain how wetlands form"],
                "To show that young people can help solve real problems",
                "The passage's focus on the students' successful advocacy reveals this purpose.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about the wetland after the officials' plan?",
                ["It will likely become healthier for the cranes", "It will be closed to visitors", "The cranes will stop coming entirely", "The rainfall problem will worsen"],
                "It will likely become healthier for the cranes",
                "With deeper channels and protected water, the wetland should better support the cranes' needs.",
            ),
        ],
    ),
    PassageSeed(
        title="Devika's Stories",
        body=(
            "Long before printed books existed, traveling narrators moved from village to village, sharing tales beside crackling fires. "
            "In one small mountain village, an elderly storyteller named Devika was famous for her wonderfully vivid tales. "
            "Children would gather each evening, sitting cross-legged as Devika described brave heroes and clever tricksters. "
            "One winter, Devika grew seriously ill, and villagers worried her treasured stories might soon be forgotten entirely. "
            "A young girl named Priti decided to visit Devika daily, writing down every story she remembered. "
            "At first, Devika worried that written stories would somehow lose the warmth of being spoken aloud. "
            "Priti promised to read the stories aloud exactly as Devika had once told them, word for word. "
            "Slowly, Devika recovered, delighted to discover her stories now reached even more children throughout the region. "
            "Years later, Priti's careful notebooks became treasured books, still read aloud by parents and teachers everywhere. "
            "The village never forgot that one person's effort had preserved generations of imagination and wisdom together. "
            "Every winter evening, families still gathered to read Priti's careful notebooks aloud together by the fire."
        ),
        difficulty_rank=43,
        takeaway="Writing down spoken traditions can help preserve them for future generations.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What was Devika famous for?",
                ["Her wonderfully vivid tales", "Her cooking", "Her farming skills", "Her singing"],
                "Her wonderfully vivid tales",
                "The passage says the storyteller Devika was famous for her wonderfully vivid tales.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did villagers worry about Devika's stories?",
                ["She grew seriously ill", "She moved away", "She forgot her stories", "She refused to tell them"],
                "She grew seriously ill",
                "The passage says one winter, Devika grew seriously ill, and villagers worried her stories might be forgotten.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Priti decide to do?",
                ["Write down every story Devika remembered", "Tell her own stories instead", "Move away from the village", "Stop visiting Devika"],
                "Write down every story Devika remembered",
                "The passage says Priti decided to visit Devika daily, writing down every story she remembered.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Devika worry about before Priti's promise?",
                ["Written stories losing their spoken warmth", "Priti forgetting the stories", "The village losing interest", "Running out of stories to tell"],
                "Written stories losing their spoken warmth",
                "The passage says at first, Devika worried that written stories would lose the warmth of being spoken aloud.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened after Priti promised to read the stories aloud?",
                ["Devika slowly recovered", "Devika grew more ill", "The village forgot the stories", "Priti stopped visiting"],
                "Devika slowly recovered",
                "The passage says slowly, Devika recovered, delighted that her stories now reached even more children.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'preserved' mean?",
                ["Kept safe from being lost", "Sold for money", "Changed completely", "Hidden from everyone"],
                "Kept safe from being lost",
                "Priti's effort 'preserved' the stories, meaning it kept them safe from being lost forever.",
            ),
            QuestionSeed(
                "inference",
                "Why did Devika feel delighted once she recovered?",
                ["Her stories now reached more children than before", "She no longer had to tell stories", "Priti stopped visiting her", "The village built her a new home"],
                "Her stories now reached more children than before",
                "Because the stories were now written down, they could reach a much wider audience than before.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                ["Preserving an elder's stories for future generations", "A village's winter traditions", "How to become a good storyteller", "A girl learning to read"],
                "Preserving an elder's stories for future generations",
                "The passage follows how Priti's writing down of Devika's stories preserved them for the whole village.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                ["To show how writing can preserve spoken traditions", "To criticize old storytelling methods", "To explain how books are printed", "To describe mountain villages"],
                "To show how writing can preserve spoken traditions",
                "The passage's focus on saving Devika's stories through writing reveals this purpose.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about the village's feelings toward stories?",
                ["They valued their stories deeply", "They found stories unimportant", "They preferred books to spoken tales", "They wanted new storytellers"],
                "They valued their stories deeply",
                "The village's worry over losing the stories and their lasting tradition of reading them shows how deeply they valued them.",
            ),
        ],
    ),
    PassageSeed(
        title="The Coral Reef",
        body=(
            "Deep beneath the ocean's surface, coral reefs quietly support an enormous variety of colorful fish and creatures. "
            "Marine biologist Doctor Sen had studied one particular reef near the coast for nearly fifteen careful years. "
            "Recently, she noticed the reef's normally vibrant colors fading into a pale, worrying shade of white. "
            "Doctor Sen explained that rising ocean heat was causing widespread coral bleaching across many reefs worldwide. "
            "Worried local fishermen, who depended on the healthy reef for their daily catch, asked her for advice. "
            "Doctor Sen suggested creating a protected zone where fishing would be limited, allowing the coral time to recover. "
            "Some fishermen hesitated, fearing the new rules would immediately hurt their already modest daily income. "
            "After lengthy community meetings, most fishermen finally agreed to try the protected zone for two full years. "
            "Slowly, over many months, patches of coral began regaining their bright, healthy colors once again. "
            "Doctor Sen often reminded the fishermen that protecting the reef today ensured their livelihoods for many years ahead. "
            "The whole town later celebrated when the reef was declared fully healthy once more."
        ),
        difficulty_rank=44,
        takeaway="Protecting nature today can secure people's livelihoods for the future.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What did Doctor Sen study for nearly fifteen years?",
                ["A particular coral reef", "A type of fish", "Ocean currents", "A fishing village"],
                "A particular coral reef",
                "The passage says Doctor Sen had studied one particular reef near the coast for nearly fifteen years.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why was the reef's color fading to white?",
                ["Rising ocean heat was causing coral bleaching", "Too many fish were living there", "Fishermen were damaging the reef", "The water was too clean"],
                "Rising ocean heat was causing coral bleaching",
                "The passage says Doctor Sen explained that rising ocean heat was causing widespread coral bleaching.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Doctor Sen suggest creating?",
                ["A protected zone with limited fishing", "A new fishing village", "A larger reef nearby", "A fish market"],
                "A protected zone with limited fishing",
                "The passage says Doctor Sen suggested creating a protected zone where fishing would be limited.",
            ),
            QuestionSeed(
                "sequencing",
                "What did fishermen do after lengthy community meetings?",
                ["Agreed to try the protected zone", "Refused the plan completely", "Left the fishing industry", "Built a new reef"],
                "Agreed to try the protected zone",
                "The passage says after lengthy community meetings, most fishermen finally agreed to try the protected zone.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did some fishermen hesitate about the protected zone?",
                ["They feared it would hurt their income", "They didn't believe in coral bleaching", "They disliked Doctor Sen", "They wanted a bigger zone"],
                "They feared it would hurt their income",
                "The passage says some fishermen hesitated, fearing the new rules would immediately hurt their daily income.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'livelihoods' mean?",
                ["Ways of earning a living", "Types of sea creatures", "Ocean temperatures", "Fishing tools"],
                "Ways of earning a living",
                "'Livelihoods' refers to the ways people, like fishermen, earn their living.",
            ),
            QuestionSeed(
                "inference",
                "Why did Doctor Sen remind fishermen that protecting the reef helped their future?",
                ["A healthy reef supports fish they depend on", "She wanted to stop all fishing forever", "She disliked the fishing community", "The reef needed no more care"],
                "A healthy reef supports fish they depend on",
                "A healthy reef sustains the fish population fishermen rely on, linking conservation to their long-term livelihood.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                ["Protecting a coral reef through community cooperation", "The daily life of fishermen", "How coral reefs form", "Ocean temperatures around the world"],
                "Protecting a coral reef through community cooperation",
                "The passage follows how Doctor Sen and the fishermen worked together to save the reef.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                ["To show how cooperation can help protect nature", "To criticize fishermen for overfishing", "To explain ocean currents", "To describe different fish species"],
                "To show how cooperation can help protect nature",
                "The passage's focus on the successful partnership between the scientist and fishermen reveals this purpose.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about the fishermen by the end of the passage?",
                ["They came to value protecting the reef", "They regretted trying the protected zone", "They stopped fishing altogether", "They blamed Doctor Sen for their losses"],
                "They came to value protecting the reef",
                "The town's celebration of the reef's recovery suggests the fishermen came to appreciate the value of protecting it.",
            ),
        ],
    ),
    PassageSeed(
        title="Arjun's Choice",
        body=(
            "Every generation in Arjun's family had worked as skilled potters, shaping clay into beautiful, useful pots. "
            "Arjun, however, felt far more drawn to computers than to the wheel in his father's workshop. "
            "His father hoped Arjun would continue the family tradition, just as his own father once had. "
            "One afternoon, Arjun nervously admitted that he dreamed of studying computer science instead of pottery. "
            "His father fell silent for a long moment, clearly upset but trying not to show it. "
            "Later that evening, Arjun's grandmother reminded her son that traditions must sometimes bend to survive. "
            "She suggested that Arjun could use his computer skills to sell the family's pottery online instead. "
            "Intrigued, Arjun built a simple website showing his father's handmade pots to customers across the country. "
            "Within months, unexpected orders poured in from cities the family had never visited before. "
            "His father finally understood that honoring tradition did not always mean following the exact same path. "
            "He began showing customers the very same website his son had built for the family. "
            "Neighbors joked that the potter's workshop had become the busiest shop in the village."
        ),
        difficulty_rank=45,
        takeaway="New skills can help honor and strengthen an old family tradition.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What had every generation in Arjun's family worked as?",
                ["Skilled potters", "Farmers", "Fishermen", "Teachers"],
                "Skilled potters",
                "The passage says every generation in Arjun's family had worked as skilled potters.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did Arjun's father fall silent?",
                ["Arjun said he wanted to study computer science instead of pottery", "Arjun broke a pot", "Arjun refused to work at all", "Arjun wanted to move away"],
                "Arjun said he wanted to study computer science instead of pottery",
                "The passage says Arjun admitted he dreamed of studying computer science, and his father fell silent, clearly upset.",
            ),
            QuestionSeed(
                "literal_recall",
                "Who reminded Arjun's father that traditions must sometimes bend?",
                ["Arjun's grandmother", "Arjun's mother", "Arjun's teacher", "Arjun's uncle"],
                "Arjun's grandmother",
                "The passage says Arjun's grandmother reminded her son that traditions must sometimes bend to survive.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Arjun do after his grandmother's suggestion?",
                ["Built a website for his father's pottery", "Stopped studying computers", "Left the family business", "Refused to help his father"],
                "Built a website for his father's pottery",
                "The passage says Arjun built a simple website showing his father's handmade pots to customers.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did unexpected orders start pouring in?",
                ["Customers found the pottery through Arjun's website", "The family lowered their prices", "A newspaper wrote about them", "They opened a new shop"],
                "Customers found the pottery through Arjun's website",
                "The passage says within months, unexpected orders poured in from cities, connecting to Arjun's new website.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'intrigued' mean?",
                ["Curious and interested", "Angry and upset", "Bored and tired", "Confused and lost"],
                "Curious and interested",
                "Arjun was 'intrigued,' meaning curious and interested in his grandmother's idea.",
            ),
            QuestionSeed(
                "inference",
                "Why did Arjun's father finally understand something new?",
                ["He saw tradition could be honored in a new way", "He decided pottery was no longer needed", "He wanted Arjun to quit computers", "He realized selling pots was pointless"],
                "He saw tradition could be honored in a new way",
                "Seeing Arjun's website help the family business showed his father that tradition can adapt without being lost.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                ["Blending tradition with new skills to help a family business", "Learning to make pottery", "Building a website step by step", "A family argument about careers"],
                "Blending tradition with new skills to help a family business",
                "The passage follows how Arjun's computer skills helped preserve his family's pottery tradition in a new way.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                ["To show that tradition and new skills can work together", "To argue that old traditions should end", "To explain how pottery is made", "To criticize modern technology"],
                "To show that tradition and new skills can work together",
                "The passage's resolution, where Arjun's tech skills support his family's tradition, reveals this purpose.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about Arjun's relationship with his father by the end?",
                ["It grew stronger through mutual understanding", "It became more distant", "Arjun left the family business entirely", "His father stopped making pottery"],
                "It grew stronger through mutual understanding",
                "Both showing pride in the website and pottery together suggests their relationship grew closer through understanding.",
            ),
        ],
    ),
    PassageSeed(
        title="The Banyan Tree",
        body=(
            "For centuries, a towering banyan tree has stood at the center of a small southern village. "
            "Villagers considered the tree sacred, gathering beneath its wide branches for festivals, meetings, and quiet talk. "
            "When a new highway project threatened to cut through the village, engineers marked the tree for removal. "
            "Furious villagers gathered signatures, wrote letters, and organized protests to save their ancient tree. "
            "Local officials argued that rerouting the highway would cost more money and delay the project a great deal. "
            "An elderly village leader calmly explained that the tree represented generations of shared memory. "
            "After weeks of tense talks, engineers finally agreed to redesign the highway around the ancient tree. "
            "Though the new route cost more and took longer to build, villagers felt deeply relieved. "
            "Today, travelers passing through still pause beneath the enormous tree, unaware of the battle once fought there. "
            "The village considers this quiet victory proof that some things matter more than cost. "
            "Visitors are surprised to learn that a whole road was redesigned to protect one tree. "
            "Children in the village grow up hearing the proud story of how their tree was saved."
        ),
        difficulty_rank=46,
        takeaway="A community's shared history can be worth protecting, even at extra cost.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Where has the banyan tree stood for centuries?",
                ["At the center of a small southern village", "Near a city hospital", "Beside a river", "Outside a school"],
                "At the center of a small southern village",
                "The passage says the banyan tree has stood at the center of a small southern village for centuries.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did engineers mark the tree for removal?",
                ["A new highway project threatened to cut through the village", "The tree was diseased", "The village asked them to", "The tree blocked a school"],
                "A new highway project threatened to cut through the village",
                "The passage says when a new highway project threatened to cut through the village, engineers marked the tree for removal.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did furious villagers do to save the tree?",
                ["Gathered signatures and organized protests", "Cut down the tree themselves", "Moved to another village", "Ignored the highway project"],
                "Gathered signatures and organized protests",
                "The passage says furious villagers gathered signatures, wrote letters, and organized protests to save their tree.",
            ),
            QuestionSeed(
                "sequencing",
                "What did engineers agree to after weeks of tense talks?",
                ["Redesign the highway around the tree", "Remove the tree immediately", "Cancel the highway entirely", "Build a smaller road"],
                "Redesign the highway around the tree",
                "The passage says after weeks of tense talks, engineers finally agreed to redesign the highway around the tree.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did local officials initially resist rerouting the highway?",
                ["It would cost more money and take longer", "They disliked the village", "The tree was not important to them", "They wanted to remove all trees"],
                "It would cost more money and take longer",
                "The passage says local officials argued that rerouting the highway would cost more money and delay the project.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'sacred' mean?",
                ["Deeply respected and valued", "Old and broken", "Dangerous and feared", "Owned by the government"],
                "Deeply respected and valued",
                "Villagers considered the tree 'sacred,' meaning deeply respected and valued.",
            ),
            QuestionSeed(
                "inference",
                "Why did the village leader say the tree represented shared memory?",
                ["Generations had gathered beneath it for important moments", "The tree was the oldest in the country", "The tree was planted by the government", "No one remembered why the tree mattered"],
                "Generations had gathered beneath it for important moments",
                "Since villagers used the tree for festivals and meetings across generations, it held collective memories for the community.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                ["A village saving a tree that matters to their community", "How highways are built", "The history of banyan trees", "A disagreement between engineers"],
                "A village saving a tree that matters to their community",
                "The passage follows the village's fight to protect a tree meaningful to their shared history.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                ["To show that some things matter more than cost or convenience", "To explain highway engineering", "To criticize village life", "To describe banyan tree biology"],
                "To show that some things matter more than cost or convenience",
                "The passage's closing message directly states this lesson.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about the village's values?",
                ["They value shared history and tradition highly", "They care only about modern roads", "They dislike change of any kind", "They prefer cost savings over anything else"],
                "They value shared history and tradition highly",
                "Their determined fight to save a tree tied to their shared memory shows how highly they value history and tradition.",
            ),
        ],
    ),
    PassageSeed(
        title="Bimal the Guide",
        body=(
            "Every monsoon, heavy rains transform a normally quiet mountain trail into a slippery, treacherous path. "
            "Local guide Bimal had walked this trail safely thousands of times throughout his many years of guiding. "
            "One rainy afternoon, while leading a group of tourists, Bimal noticed dark clouds gathering rapidly overhead. "
            "Sensing danger, he insisted the group turn back immediately, despite their visible upset and mild protest. "
            "Some tourists grumbled, insisting they had traveled far and deserved to reach the scenic summit. "
            "Bimal firmly explained that reaching the summit meant nothing if the group never returned safely. "
            "Minutes after they began their descent, a sudden landslide swept violently across the exact trail ahead. "
            "Shaken, the tourists finally understood why Bimal had insisted so firmly on turning back. "
            "That evening, the group thanked Bimal, admitting his caution had likely saved every one of their lives. "
            "Bimal simply smiled, saying that experience had taught him to always trust the mountain's subtle warnings. "
            "He added that no view, however beautiful, was ever worth risking a group's safety. "
            "From that day on, the tourists told everyone they knew about the guide who had saved their lives."
        ),
        difficulty_rank=47,
        takeaway="Experience and caution can matter more than reaching a destination.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What does Bimal do for a living?",
                ["He guides tourists on a mountain trail", "He fixes cars", "He teaches school", "He fishes for a living"],
                "He guides tourists on a mountain trail",
                "The passage says local guide Bimal had walked this trail safely thousands of times throughout his years of guiding.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did Bimal insist the group turn back?",
                ["He sensed danger from dark clouds gathering", "He was tired from walking", "The tourists asked to leave", "It was getting dark"],
                "He sensed danger from dark clouds gathering",
                "The passage says sensing danger, he insisted the group turn back after noticing dark clouds gathering rapidly.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did some tourists want to do instead of turning back?",
                ["Reach the scenic summit", "Return to their hotel", "Take photographs", "Rest at the trailhead"],
                "Reach the scenic summit",
                "The passage says some tourists grumbled, insisting they deserved to reach the scenic summit.",
            ),
            QuestionSeed(
                "sequencing",
                "What happened minutes after the group began their descent?",
                ["A sudden landslide swept across the trail", "The rain stopped completely", "The tourists reached the summit", "Bimal fell behind the group"],
                "A sudden landslide swept across the trail",
                "The passage says minutes after they began their descent, a sudden landslide swept violently across the trail.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why were the tourists shaken after the landslide?",
                ["They realized Bimal's caution had saved them", "They were injured by rocks", "They lost their belongings", "They were far from the trailhead"],
                "They realized Bimal's caution had saved them",
                "The passage says shaken, the tourists finally understood why Bimal had insisted so firmly on turning back.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'treacherous' mean?",
                ["Dangerous and unpredictable", "Smooth and easy", "Colorful and scenic", "Narrow and short"],
                "Dangerous and unpredictable",
                "A 'treacherous' path is one that is dangerous and unpredictable, especially during monsoon rains.",
            ),
            QuestionSeed(
                "inference",
                "Why did Bimal say experience taught him to trust the mountain's warnings?",
                ["His years of guiding helped him sense danger early", "He had read about landslides in a book", "A weather report warned him", "Another guide told him to leave"],
                "His years of guiding helped him sense danger early",
                "Bimal's long experience on the trail gave him the instinct to recognize danger signs like the gathering clouds.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                ["A guide's experience keeping tourists safe from danger", "How landslides form on mountains", "A group's disappointment about a canceled trip", "The history of mountain trails"],
                "A guide's experience keeping tourists safe from danger",
                "The passage centers on how Bimal's caution and experience protected the tourists from a serious danger.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                ["To show the value of experience and caution over impatience", "To describe mountain scenery", "To criticize tourists in general", "To explain how guides are trained"],
                "To show the value of experience and caution over impatience",
                "The passage's outcome, where caution proves lifesaving, reveals this purpose.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about Bimal's character?",
                ["He values safety over the tourists' immediate wishes", "He does not care what tourists think", "He avoids making difficult decisions", "He is unfamiliar with the trail's dangers"],
                "He values safety over the tourists' immediate wishes",
                "Despite the tourists' protests, Bimal prioritized their safety, showing his commitment to protecting them above all else.",
            ),
        ],
    ),
    PassageSeed(
        title="Ravi's Two Boats",
        body=(
            "In a small coastal town, fishermen had long relied on traditional wooden boats passed down through families. "
            "When a government program offered modern motorized boats at a discount, opinions throughout the town divided sharply. "
            "Older fishermen worried that switching boats would disrespect generations of hard-earned fishing knowledge. "
            "Younger fishermen argued that motorized boats would let them travel farther and catch far more fish. "
            "Ravi, a respected middle-aged fisherman, found himself torn awkwardly between honoring tradition and embracing practical, obvious progress. "
            "After much careful thought, Ravi decided to purchase one motorized boat while still keeping his father's old wooden one. "
            "He used the new boat for longer trips, while the old boat still carried deep value. "
            "Slowly, other fishermen noticed Ravi's balanced approach and began trying similar solutions for their own families. "
            "Within a few years, the town's fishing income improved a lot, without the old wooden boats vanishing. "
            "Ravi often said that progress and tradition could coexist, given enough patience and respect. "
            "His father's old wooden boat still hangs proudly above the door of Ravi's small seaside home. "
            "Younger fishermen now visit Ravi for advice whenever they face a hard choice of their own."
        ),
        difficulty_rank=48,
        takeaway="Progress and tradition can work together instead of replacing one another.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What had fishermen in the town long relied on?",
                ["Traditional wooden boats", "Motorized boats only", "Fishing nets alone", "Large fishing ships"],
                "Traditional wooden boats",
                "The passage says fishermen had long relied on traditional wooden boats passed down through families.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did older fishermen worry about motorized boats?",
                ["They feared it would disrespect traditional knowledge", "They could not afford them", "They disliked loud engines", "They preferred fishing alone"],
                "They feared it would disrespect traditional knowledge",
                "The passage says older fishermen worried that switching boats would disrespect generations of traditional fishing knowledge.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did the younger generation believe the new technology would help them do?",
                ["They would let them travel farther and catch more fish", "They were more expensive", "They looked nicer", "They were quieter"],
                "They would let them travel farther and catch more fish",
                "The passage says younger fishermen argued that motorized boats would let them travel farther and catch more fish.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Ravi do after much careful thought?",
                ["Bought a motorized boat while keeping his old wooden one", "Sold his father's boat immediately", "Refused to buy a new boat", "Stopped fishing altogether"],
                "Bought a motorized boat while keeping his old wooden one",
                "The passage says Ravi decided to purchase one motorized boat while still keeping his father's old wooden one.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did other fishermen begin trying similar solutions?",
                ["They noticed Ravi's balanced approach worked well", "They were told to by officials", "They ran out of options", "They wanted to copy his boat design"],
                "They noticed Ravi's balanced approach worked well",
                "The passage says slowly, other fishermen noticed Ravi's balanced approach and began trying similar solutions.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'coexist' mean?",
                ["Exist together at the same time", "Compete against each other", "Replace one another completely", "Disappear over time"],
                "Exist together at the same time",
                "Ravi said progress and tradition could 'coexist,' meaning they could exist together at the same time.",
            ),
            QuestionSeed(
                "inference",
                "Why did Ravi feel torn between tradition and progress?",
                ["He respected both his family's history and new opportunities", "He disliked both wooden and motorized boats", "He wanted to stop fishing entirely", "He had no opinion on the matter"],
                "He respected both his family's history and new opportunities",
                "Ravi's struggle came from valuing his family's traditional knowledge while also seeing the benefits of modern tools.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                ["Balancing tradition and progress in a fishing town", "The history of fishing boats", "A disagreement among fishermen", "How to build a motorized boat"],
                "Balancing tradition and progress in a fishing town",
                "The passage follows how Ravi's balanced choice helped the whole town blend tradition with progress.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                ["To show that tradition and progress can work together", "To argue that old methods should be abandoned", "To explain how boats are built", "To criticize younger fishermen"],
                "To show that tradition and progress can work together",
                "Ravi's closing statement about coexistence directly reveals this purpose.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about Ravi by the end of the passage?",
                ["He became a respected example for the community", "He regretted buying the new boat", "He gave up fishing entirely", "He ignored his father's wishes"],
                "He became a respected example for the community",
                "Younger fishermen now visiting Ravi for advice shows he became a respected example for others in the town.",
            ),
        ],
    ),
    PassageSeed(
        title="Saving the Library",
        body=(
            "Throughout history, city libraries have quietly served as gathering places for readers, students, and curious wandering minds. "
            "The historic central library in Meera's city announced a sudden, permanent closure due to shrinking government money. "
            "Residents across the whole city reacted to the news with genuine alarm and disbelief. "
            "Meera, an eager teenage volunteer, had spent countless peaceful afternoons reading quietly among the library's towering, dusty shelves. "
            "Refusing to simply accept the closure, Meera organized a determined group of fellow volunteers and concerned local residents. "
            "Together, they collected thousands of signatures and presented a detailed petition to the city council. "
            "Meera also helped organize a lively community fundraiser, featuring local musicians, artists, and eager young volunteers. "
            "Slowly, donations and growing public pressure convinced hesitant officials to seriously reconsider their original difficult decision. "
            "After several tense months, the council finally agreed to keep the beloved library open for good. "
            "Meera realized that ordinary citizens, when united by genuine purpose, could truly influence even difficult official decisions. "
            "The library later dedicated a small reading corner in Meera's honor, inspiring countless future young readers. "
            "Every year on the anniversary of that day, the library still holds a small celebration for her."
        ),
        difficulty_rank=49,
        takeaway="Ordinary people, working together, can influence even difficult official decisions.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "Why did the library announce its closure?",
                ["Shrinking government money", "Too many visitors", "A fire in the building", "Old and broken shelves"],
                "Shrinking government money",
                "The passage says the library announced a sudden closure due to shrinking government money.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did residents react with alarm to the announcement?",
                ["The library was important to the community", "They disliked the librarians", "They wanted a bigger library", "They had never used the library"],
                "The library was important to the community",
                "The passage's description of Meera's countless afternoons there shows how meaningful the library was to residents like her.",
            ),
            QuestionSeed(
                "literal_recall",
                "What did Meera and other volunteers collect?",
                ["Thousands of signatures for a petition", "Money for a new building", "Old books to sell", "Votes for a new mayor"],
                "Thousands of signatures for a petition",
                "The passage says together, they collected thousands of signatures and presented a detailed petition.",
            ),
            QuestionSeed(
                "sequencing",
                "What did Meera organize after collecting signatures?",
                ["A community fundraiser", "A protest march", "A new library branch", "A book sale"],
                "A community fundraiser",
                "The passage says Meera also helped organize a lively community fundraiser with local musicians and artists.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why did officials reconsider their decision?",
                ["Donations and growing public pressure convinced them", "The mayor personally asked them to", "The library offered them money", "No one visited the library anymore"],
                "Donations and growing public pressure convinced them",
                "The passage says slowly, donations and growing public pressure convinced hesitant officials to reconsider.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'hesitant' mean?",
                ["Unsure and slow to decide", "Angry and loud", "Excited and quick", "Confident and certain"],
                "Unsure and slow to decide",
                "'Hesitant' officials are ones who are unsure and slow to make a decision.",
            ),
            QuestionSeed(
                "inference",
                "Why did Meera realize citizens could influence official decisions?",
                ["Her group's efforts successfully changed the council's mind", "The council ignored her petition", "She read about it in a book", "A teacher told her so"],
                "Her group's efforts successfully changed the council's mind",
                "Seeing the council reverse its decision because of the community's actions taught Meera this lesson directly.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                ["A community coming together to save their library", "The history of city libraries", "How to organize a fundraiser", "A city council meeting"],
                "A community coming together to save their library",
                "The passage follows Meera and her community's successful campaign to keep their library open.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                ["To show that ordinary people can create real change", "To criticize government funding decisions", "To explain how libraries are built", "To describe Meera's daily routine"],
                "To show that ordinary people can create real change",
                "The passage's message about citizens influencing decisions reveals this purpose.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about Meera's impact on her community?",
                ["Her actions left a lasting, positive mark", "Her efforts were quickly forgotten", "She acted alone without any support", "The library closed despite her efforts"],
                "Her actions left a lasting, positive mark",
                "The library's yearly celebration in her honor shows her impact was lasting and meaningful.",
            ),
        ],
    ),
    PassageSeed(
        title="Waiting for Rain",
        body=(
            "Every year, dark clouds gather over the village just before the monsoon season begins. "
            "Farmers like Suresh watch the sky, hoping for the heavy showers to arrive soon. "
            "When rain finally falls, dry brown fields slowly turn into soft, muddy soil ready for planting rice. "
            "Suresh and his neighbours work together, planting rice seedlings in flooded rows across the land. "
            "Rainwater collects in ponds and slowly seeps into the thirsty ground below. "
            "Nearby rivers and lakes also fill up, and many birds return to feed in the wetlands. "
            "This stored water later helps crops grow strong even during the hot, dry months of summer. "
            "Trees and plants also depend on regular rain to grow well and make their own food. "
            "Without enough rainfall, crops can wither, wells can run dry, and farmers may struggle to earn a living. "
            "Many farmers offer small prayers of thanks when the first raindrops finally arrive. "
            "That is why many villages celebrate the monsoon season with joyful songs, dances, and festive gatherings. "
            "Children often run outside barefoot, laughing and splashing happily through the cool, refreshing puddles. "
            "For farming communities across India, the monsoon is not just weather, but a vital part of daily life."
        ),
        difficulty_rank=50,
        takeaway="The monsoon rains are essential for crops, rivers, and everyday village life.",
        questions=[
            QuestionSeed(
                "literal_recall",
                "What are Suresh and his neighbours planting?",
                ["Rice", "Wheat", "Corn", "Cotton"],
                "Rice",
                "The passage says Suresh and his neighbours were planting rice seedlings.",
            ),
            QuestionSeed(
                "literal_recall",
                "Where does rainwater seep into?",
                ["The ground", "The house", "The road", "The market"],
                "The ground",
                "The passage says rainwater seeps into the thirsty ground below.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "Why do dry fields turn into muddy soil?",
                ["Rain falls on them", "Farmers water them by hand", "The sun heats them", "Birds dig them up"],
                "Rain falls on them",
                "The passage says when rain falls, the dry fields turn into muddy soil.",
            ),
            QuestionSeed(
                "cause_and_effect",
                "What happens if there is not enough rain?",
                ["Crops can wither", "Rivers overflow", "Birds leave early", "Markets close down"],
                "Crops can wither",
                "The passage says without enough rainfall, crops can wither.",
            ),
            QuestionSeed(
                "sequencing",
                "What happens right after the first rain falls?",
                ["Dry fields turn muddy", "Villages hold festivals", "Rivers dry up", "Children go to school"],
                "Dry fields turn muddy",
                "The passage describes dry fields turning muddy right after the rain falls.",
            ),
            QuestionSeed(
                "vocabulary_in_context",
                "In the passage, what does 'wither' mean?",
                ["Dry up and weaken", "Grow bigger and stronger", "Turn a bright colour", "Move to a new field"],
                "Dry up and weaken",
                "The passage links 'wither' with crops drying up when there is not enough rain.",
            ),
            QuestionSeed(
                "inference",
                "Why do farmers offer prayers when the first raindrops arrive?",
                [
                    "They are thankful for the rain",
                    "They are afraid of storms",
                    "They want the rain to stop",
                    "They are bored with nothing else to do",
                ],
                "They are thankful for the rain",
                "Farmers depend on rain for their crops, so their prayers show thankfulness.",
            ),
            QuestionSeed(
                "main_idea",
                "What is this passage mostly about?",
                [
                    "Why the monsoon matters to village life",
                    "A trip Suresh takes to the city",
                    "A birthday party in the village",
                    "A cricket match during the rains",
                ],
                "Why the monsoon matters to village life",
                "The whole passage explains how the monsoon affects farming and village life.",
            ),
            QuestionSeed(
                "authors_purpose",
                "Why did the author most likely write this passage?",
                [
                    "To explain why the monsoon is important",
                    "To tell a scary story about floods",
                    "To describe a birthday celebration",
                    "To give directions to a village",
                ],
                "To explain why the monsoon is important",
                "The passage is written to inform readers about the importance of the monsoon.",
            ),
            QuestionSeed(
                "drawing_conclusions",
                "What can you conclude about people who live in this village?",
                [
                    "Their lives depend a lot on rain",
                    "They never grow any crops",
                    "They dislike the rainy season",
                    "They only work indoors",
                ],
                "Their lives depend a lot on rain",
                "Farming, water, and festivals in the passage all connect back to rain.",
            ),
        ],
    ),
]


def _to_passage_detail(seed: PassageSeed) -> PassageDetail:
    now = datetime.now(timezone.utc)
    questions = [
        ComprehensionQuestionSchema(
            id=uuid.uuid4(),
            passage_id=uuid.uuid4(),  # placeholder -- not yet linked to a real passage row
            question_type=q.question_type,
            question_text=q.question_text,
            options=q.options,
            correct_answer=q.correct_answer,
            explanation_hint=q.explanation_hint,
        )
        for q in seed.questions
    ]
    return PassageDetail(
        id=uuid.uuid4(),
        subject="english",
        title=seed.title,
        body=seed.body,
        word_count=len(seed.body.split()),
        sentence_count=_sentence_count(seed.body),
        difficulty_rank=seed.difficulty_rank,
        takeaway=seed.takeaway,
        created_at=now,
        questions=questions,
    )


def _insert_passage(db, seed: PassageSeed, detail: PassageDetail) -> None:
    passage = Passage(
        subject="english",
        title=seed.title,
        body=seed.body,
        word_count=detail.word_count,
        sentence_count=detail.sentence_count,
        difficulty_rank=seed.difficulty_rank,
        takeaway=seed.takeaway,
    )
    db.add(passage)
    db.flush()
    for q in seed.questions:
        db.add(
            ComprehensionQuestion(
                passage_id=passage.id,
                question_type=q.question_type,
                question_text=q.question_text,
                options=q.options,
                correct_answer=q.correct_answer,
                explanation_hint=q.explanation_hint,
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run validate_passage() and print the report without writing to the database",
    )
    args = parser.parse_args()

    all_clean = True
    details = []
    for seed in PASSAGES:
        detail = _to_passage_detail(seed)
        problems = validate_passage(detail)
        details.append((seed, detail))

        status = "CLEAN" if not problems else f"{len(problems)} PROBLEM(S)"
        print(f"\n=== Rank {seed.difficulty_rank}: {seed.title} [{status}] ===")
        print(
            f"  word_count={detail.word_count}  sentence_count={detail.sentence_count}  "
            f"questions={len(seed.questions)}"
        )
        for problem in problems:
            print(f"  - {problem}")
            all_clean = False

    print(
        "\n"
        + (
            f"All {len(PASSAGES)} passages passed validate_passage()."
            if all_clean
            else "Some passages failed validation."
        )
    )

    if args.validate_only:
        return
    if not all_clean:
        print("Refusing to write to the database because validation failed.")
        raise SystemExit(1)

    db = SessionLocal()
    try:
        for seed, detail in details:
            _insert_passage(db, seed, detail)
        db.commit()
        print(f"Inserted {len(PASSAGES)} passages into the database.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
