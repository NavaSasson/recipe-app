
// Fetch and display recipes
async function fetchRecipes(category = '') {
    try {
        const url = category 
            ? `/recipe/category/${category}`
            : '/recipe';
        const response = await fetch(url);
        const recipes = await response.json();
        displayRecipes(recipes);
    } catch (error) {
        console.error('Error fetching recipes:', error);
    }
}

// Display recipes in the grid
function displayRecipes(recipes) {
    const container = document.getElementById('recipeContainer');
    container.innerHTML = '';

    recipes.forEach(recipe => {
        const card = document.createElement('div');
        card.className = 'recipe-card';
        card.innerHTML = `
            <h3>${recipe.name}</h3>
            <p><strong>Category:</strong> ${recipe.category}</p>
            <p><strong>Ingredients:</strong></p>
            <ul>
                ${recipe.ingredients.map(ing => `<li>${ing}</li>`).join('')}
            </ul>
            <p><strong>Steps:</strong></p>
            <ol>
                ${recipe.steps.map(step => `<li>${step}</li>`).join('')}
            </ol>
            <button onclick="deleteRecipe('${recipe._id}')">Delete</button>
        `;
        container.appendChild(card);
    });
}

// Filter recipes by category
function filterByCategory() {
    const category = document.getElementById('category').value;
    fetchRecipes(category);
}

// Submit new recipe
async function submitRecipe(event) {
    event.preventDefault();

    const recipe = {
        name: document.getElementById('name').value,
        category: document.getElementById('recipeCategory').value,
        ingredients: document.getElementById('ingredients').value.split(',').map(i => i.trim()),
        steps: document.getElementById('steps').value.split(',').map(s => s.trim())
    };

    try {
        const response = await fetch('/recipe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(recipe)
        });

        if (response.ok) {
            event.target.reset();
            fetchRecipes();
        } else {
            console.error('Error creating recipe');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Delete recipe
async function deleteRecipe(id) {
    try {
        const response = await fetch(`/recipe/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            fetchRecipes();
        } else {
            console.error('Error deleting recipe');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    fetchRecipes();
});