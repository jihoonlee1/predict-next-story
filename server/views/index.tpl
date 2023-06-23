<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<link rel="stylesheet" href="/static/index.css"/>
	<title>Predict Next Story - Sustainalytics</title>
</head>
<body>
	<header>
		<div>
			<h1>Predicting Next Story</h1>
			<img src="/static/sust_logo.svg"/>
		</div>
	</header>
	<section>
		<h2>Demo</h2>
		<p>The description is written below. If you would just like to test the model, please give a try. You are testing whether the second sentence is a follow up to the first sentence.</p>
		<form>
			<label for="sentence1">
				<span>sentence_1: </span>
				<br/>
				<input type="text" name="sentence1" id="sentence1" placeholder="Justin gets bitten by a mosquito." required/>
			</label>
			<label for="sentence2">
				<span>sentence_2: </span>
				<br/>
				<input type="text" name="sentence2" id="sentence2" placeholder="Justin is hospitalized after getting bitten by a mosquito." required/>
			</label>
			<div>
				<button type="submit">Submit</button>
				<button type="reset">Clear Text</button>
			</div>
			<div>
				<p>output:</p>
				<span>
					<span>likelihood_to_yes:</span>
					<span id="yes-next"></span>
				</span>
				<br/>
				<span>
					<span>likelihood_to_no: </span>
					<span id="no-next"></span>
				</span>
			</div>
		</form>
	</section>
	<section>
		<h2>Introduction</h2>
		<p>With the intention of emulating the immersive experience of reading a book, our team delved into the development of an automation tool aimed at grouping disorganized clusters of events into coherent chains. In this interconnected chain, each event seamlessly leads to the next, allowing for a smooth progression of the narrative. The primary objective behind this automation endeavor was to facilitate the visualization of events, enabling users to gain a clear understanding of their origin and current state effortlessly.</p>
	</section>
	<section>
		<h2>Data Preparation</h2>
		<p>Around 2000 well-known companies were gathered from <a href="https://www.forbes.com/lists/global2000/?sh=7b7bfbf65ac0" target="_blank">Forbes</a>. For each companies, these questions were asked through gpt-4 engine:</p>
		<ul>
			<li>Write 5 news stories about &#60;<strong>company_name</strong>&#62; on different subject.</li>
			<li>For each story above, write news stories about &#60;<strong>company_name</strong>&#62; that are considered as direct follow-ups to the story. Write each story from company_name's perspective.<em>This is considered as soft-positive.</em></li>
			<li>For each story above, write news stories about &#60;<strong>company_name</strong>&#62; that are considered as direct follow-ups to the story. Write each story from a different company's perspective.<em>This is considered as hard-positive.</em></li>
			<li>For each story above, write news stories about &#60;<strong>company_name</strong>&#62; that are irrelevant to the story. <em>This is considered as soft-negative.</em></li>
		</ul>
		<p>Since ChatGPT API was a paid service & pricy, I ended up <a href="https://github.com/jihoonlee1/bingchat" target="_blank">reverse-engineering</a> another gpt-4 engine, called <a href="https://www.bing.com/new" target="_blank">Bing Chat</a> from Microsoft.</p>
		<p>After preparing the data with gpt-4 engine, more custom data were prepared.</p>
		<ul>
			<li>For each soft-positive data, I used NER to detect the company within the context, then replacing the company with a different company while keeping all the context the same. <em>This was hard-negative dataset</em>.
				<p>
					<strong>Goldman Sachs Group</strong> has reached a $3.9 billion settlement with the Malaysian government over its role in the 1Malaysia Development Berhad scandal...<br/>
					<strong>Teradyne</strong> has reached a $3.9 billion settlement with the Malaysian government over its role in the 1Malaysia Development Berhad scandal...
				</p>
			</li>
			<li>For each soft-positve data, I once again used NER to detect entities other than the company itself, then replacing them with other entities while keeping all the context the same.<em>This was another hard-negative dataset</em>.</li>
			<p>
				Goldman Sachs Group has reached a $3.9 billion settlement with the Malaysian government over its role in the <strong>1Malaysia Development Berhad</strong> scandal...<br/>
				Goldman Sachs Group has reached a $3.9 billion settlement with the Malaysian government over its role in the <strong>China Citic Bank</strong> scandal...
			</p>
		</ul>
		<p>At the end of the day, I ended up gathering around 30,000 data.</p>
	</section>
	<section>
		<h2>Training</h2>
		<p>About 90% of the dataset were used (28,591) for training.</p>
		<p><a href="https://en.wikipedia.org/wiki/BERT_(language_model)" target="_blank">BERT</a> base model was used to fine-tune to meet our goal. These parameters were used for training.</p>
		<ul>
			<li>optimizer: Adam</li>
			<li>learning rate: 0.00003</li>
			<li>loss function: Binary Cross Entropy (with logits loss)</li>
			<li>batch size: 4</li>
			<li>epochs: 10</li>
		</ul>
		<p>The training was done on my personal PC, CUDA enabled with GeForce 3060ti graphic card. The whole training took about 18 hours.</p>
	</section>
	<section>
		<h2>Testing</h2>
		<p>The rest of 10% of the dataset (3,177) were used for testing. From the test dataset, the best model out of ten epochs resulted average_loss of <em>0.135</em> and accuracy of <em>0.952</em>.</p>
		<p>At this point, I was confident enough to test the model on our real time data.</p>
	</section>
	<section>
		<h2>Testing on Real Data</h2>
		<p>Our team is responsible for maintaining <a href="https://github.com/Morningstar/SUST-News-Harvesting-System-QA" target="_blank">harvesting module</a> through LexisNexis. After parsing and running the news through few models, we use our <a href="https://github.com/Morningstar/NATE-CLUSTERING" target="_blank">clustering</a> algorithm to group news articles into bubbles; we call this an <em>incident</em>. The bigger the bubble is, the higher likelihood that the incident is controversal or severe, meaning that more news source talk about this certain incident.</p>
		<p>Current clustered data from our NATE database were used through the model. Here were some of the results:</p>
		<figure>
			<img src="/static/0.png"/>
			<figcaption>This event talks about the outbreak of Ebola in Republic of Congo.</figcaption>
		</figure>
		<figure>
			<img src="/static/1.png"/>
			<figcaption>This event talks about Monkeypox across Europe. Luckily, this did not overlap with the Ebola event above.</figcaption>
		</figure>
		<figure>
			<img src="/static/2.png"/>
			<figcaption>Disney losing its copyright to Mickey Mouse.</figcaption>
		</figure>
		<figure>
			<img src="/static/3.png"/>
			<figcaption>About Disney employee getting fired for not getting COVID vaccine and not wearing mask due to a religious reason.</figcaption>
		</figure>
		<figure>
			<img src="/static/4.png"/>
			<figcaption>Shell and Quatar collaborating for LNG.</figcaption>
		</figure>
		<figure>
			<img src="/static/5.png"/>
			<figcaption>Shell building hydrogen plant in Netherlands.</figcaption>
		</figure>
		<p>These are just few examples. There must be multiple cases where the model seeks for improvements.</p>
		<p>For chaining the incidents, the following rules were used:</p>
		<ul>
			<li>The incident must be published within two months relative the incident right above.</li>
			<li>The sigmoid output comparing two incidents must be greater than or equal to 0.95.</li>
			<li>If the incident is already been chained into an event, then the incident cannot be chained into a different event.</li>
		</ul>
	</section>
	<footer><span>Powered By NATE Team @ <a href="https://www.sustainalytics.com/" target="_blank">Sustainalytics</a></span></footer>
	<script src="/static/index.js"></script>
</body>
</html>
