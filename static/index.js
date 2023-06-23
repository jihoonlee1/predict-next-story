const form = document.querySelector("form");
const yesNext = document.getElementById("yes-next");
const noNext = document.getElementById("no-next");


form.onsubmit = async function(e)
{
	e.preventDefault();
	const res = await fetch("/api/predict", {
		method: "POST",
		body: new FormData(form)
	});
	const json = await res.json();
	const [yes, no] = json;
	yesNext.textContent = yes;
	noNext.textContent = no;
}