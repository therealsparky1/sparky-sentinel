// Todo List Frontend Logic - Built by Sparky

const API_URL = 'http://localhost:3000/api/todos';
let currentFilter = 'all';
let todos = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  loadTodos();
  setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
  // Enter key to add todo
  document.getElementById('todoTitle').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      addTodo();
    }
  });

  // Filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderTodos();
    });
  });
}

// Load todos from API
async function loadTodos() {
  try {
    const response = await fetch(API_URL);
    const data = await response.json();
    todos = data.todos || [];
    renderTodos();
  } catch (error) {
    console.error('Error loading todos:', error);
    showError('Failed to load todos');
  }
}

// Add new todo
async function addTodo() {
  const title = document.getElementById('todoTitle').value.trim();
  const description = document.getElementById('todoDescription').value.trim();

  if (!title) {
    alert('Please enter a title');
    return;
  }

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description })
    });

    if (response.ok) {
      document.getElementById('todoTitle').value = '';
      document.getElementById('todoDescription').value = '';
      await loadTodos();
    } else {
      throw new Error('Failed to add todo');
    }
  } catch (error) {
    console.error('Error adding todo:', error);
    showError('Failed to add todo');
  }
}

// Toggle todo completion
async function toggleTodo(id) {
  const todo = todos.find(t => t.id === id);
  if (!todo) return;

  try {
    const response = await fetch(`${API_URL}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed: !todo.completed })
    });

    if (response.ok) {
      await loadTodos();
    } else {
      throw new Error('Failed to update todo');
    }
  } catch (error) {
    console.error('Error updating todo:', error);
    showError('Failed to update todo');
  }
}

// Delete todo
async function deleteTodo(id) {
  if (!confirm('Delete this todo?')) return;

  try {
    const response = await fetch(`${API_URL}/${id}`, {
      method: 'DELETE'
    });

    if (response.ok) {
      await loadTodos();
    } else {
      throw new Error('Failed to delete todo');
    }
  } catch (error) {
    console.error('Error deleting todo:', error);
    showError('Failed to delete todo');
  }
}

// Clear completed todos
async function clearCompleted() {
  const completedTodos = todos.filter(t => t.completed);
  if (completedTodos.length === 0) {
    alert('No completed todos to clear');
    return;
  }

  if (!confirm(`Delete ${completedTodos.length} completed todo(s)?`)) return;

  try {
    await Promise.all(
      completedTodos.map(todo => 
        fetch(`${API_URL}/${todo.id}`, { method: 'DELETE' })
      )
    );
    await loadTodos();
  } catch (error) {
    console.error('Error clearing completed todos:', error);
    showError('Failed to clear completed todos');
  }
}

// Render todos to DOM
function renderTodos() {
  const todoList = document.getElementById('todoList');
  
  // Filter todos
  let filteredTodos = todos;
  if (currentFilter === 'active') {
    filteredTodos = todos.filter(t => !t.completed);
  } else if (currentFilter === 'completed') {
    filteredTodos = todos.filter(t => t.completed);
  }

  // Empty state
  if (filteredTodos.length === 0) {
    todoList.innerHTML = `
      <div class="empty-state">
        ${currentFilter === 'completed' ? 'No completed todos' : 'No todos yet. Add one above!'}
      </div>
    `;
    updateStats();
    return;
  }

  // Render todo items
  todoList.innerHTML = filteredTodos.map(todo => `
    <div class="todo-item" data-id="${todo.id}">
      <input 
        type="checkbox" 
        class="todo-checkbox" 
        ${todo.completed ? 'checked' : ''}
        onchange="toggleTodo(${todo.id})"
      />
      <div class="todo-content">
        <div class="todo-title ${todo.completed ? 'completed' : ''}">
          ${escapeHtml(todo.title)}
        </div>
        ${todo.description ? `
          <div class="todo-description">${escapeHtml(todo.description)}</div>
        ` : ''}
      </div>
      <div class="todo-actions">
        <button onclick="deleteTodo(${todo.id})">Delete</button>
      </div>
    </div>
  `).join('');

  updateStats();
}

// Update stats display
function updateStats() {
  const activeTodos = todos.filter(t => !t.completed).length;
  const totalTodos = todos.length;
  document.getElementById('todoCount').textContent = 
    `${activeTodos} of ${totalTodos} item${totalTodos !== 1 ? 's' : ''}`;
}

// Show error message
function showError(message) {
  const todoList = document.getElementById('todoList');
  todoList.innerHTML = `
    <div class="empty-state" style="color: #ef4444;">
      ❌ ${message}<br>
      <small>Check console for details</small>
    </div>
  `;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
