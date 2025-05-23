document.addEventListener('DOMContentLoaded', () => {
  // Password confirmation check (for Register and Edit Profile pages)
  const form = document.querySelector('form');
  if (form) {
    const pwd = form.querySelector('input[name="password"]');
    const confirmPwd = form.querySelector('input[name="confirm_password"]');
    
    if (pwd && confirmPwd) {
      form.addEventListener('submit', (e) => {
        if (pwd.value !== confirmPwd.value) {
          e.preventDefault();
          alert("❌ Passwords do not match.");
          pwd.focus();
        }
      });
    }
  }

  // Budget alerts on dashboard
  const totalExpenseElem = document.querySelector('meta[name="total-expense"]');
  const budgetElem = document.querySelector('meta[name="budget-limit"]');

  if (totalExpenseElem && budgetElem) {
    const totalExpense = parseFloat(totalExpenseElem.content);
    const budget = parseFloat(budgetElem.content);

    if (!isNaN(totalExpense) && !isNaN(budget)) {
      if (totalExpense > budget) {
        alert("❌ You have exceeded your budget limit!");
      } else if (totalExpense > 0.75 * budget) {
        const percent = Math.round((totalExpense / budget) * 100);
        alert(`⚠️ Warning: You’ve used ${percent}% of your budget.`);
      }
    }
  }
});

