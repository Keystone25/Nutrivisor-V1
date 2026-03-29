const newsContainer = document.getElementById("news");


window.addEventListener("DOMContentLoaded", () => {
  
  fetch(`https://newsapi.org/v2/top-headlines?country=in&category=health&apiKey=df7b877109524599a7998944ecda0fd6`)
.then((response) => response.json())
.then((data) => {
        
        newsContainer.innerHTML = "";

        
        data.articles.forEach((article) => {
          
          const newsCard = document.createElement("div");
          newsCard.className = "w3-card-4 w3-margin-bottom";
          
          newsCard.innerHTML = `
            <img src="${article.urlToImage}" class="w3-image" style="width: 100%" alt="${article.title}">
            <div class="w3-container w3-padding">
              <h5 class="w3-text-black">${article.title}</h5>
              <p class="w3-text-grey">${article.description}</p>
              <a href="${article.url}" target="_blank" class="w3-button w3-blue-grey">Read more</a>
            </div>`;
          
          
          newsContainer.appendChild(newsCard);
        });
      })
      .catch((error) => {
        console.error(error);
      });
});