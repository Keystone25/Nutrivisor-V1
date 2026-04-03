const newsContainer = document.getElementById("news");

window.addEventListener("DOMContentLoaded", () => {

  fetch('https://newsdata.io/api/1/latest?apikey=pub_7f4a59bfb11640358b4d9f5587acd24d&country=in&language=en,ml&category=health,food&image=1&removeduplicate=1')
    .then(response => response.json())
    .then(data => {

      newsContainer.innerHTML = "";


      if (!data.results || data.results.length === 0) {
        newsContainer.innerHTML = "<p>No fitness/health news found.</p>";
        return;
      }

      data.results.forEach(article => {

        const newsCard = document.createElement("div");
        newsCard.className = "w3-card-4 w3-margin-bottom";

        
        const image = article.image_url 
          ? article.image_url 
          : "https://via.placeholder.com/200x100?text=Fitness+News";

        const description = article.description 
          ? article.description 
          : "No description available.";

        const link = article.link;

        newsCard.innerHTML = `
          <img src="${image}" class="w3-image" style="width:auto; height:auto; display:block; margin:auto;">
          <div class="w3-container w3-padding">
            <h5>${article.title}</h5>
            <p>${description}</p>
            <a href="${link}" target="_blank" class="w3-button w3-blue-grey">Read more</a>
          </div>
        `;

        newsContainer.appendChild(newsCard);
      });

    })
    .catch(error => {
      console.error(error);
      newsContainer.innerHTML = "<p> Failed to load news</p>";
    });

});