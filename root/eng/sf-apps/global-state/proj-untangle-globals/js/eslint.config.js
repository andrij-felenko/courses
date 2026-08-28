// eslint.config.js — годинник читають лише в корені композиції
rules: {
  "no-restricted-syntax": [
    "error",
    { selector: "NewExpression[callee.name='Date'][arguments.length=0]",
      message: "час беруть із Clock; new Date() — лише в composition root" },
    { selector: "CallExpression[callee.object.name='Date'][callee.property.name='now']",
      message: "час беруть із Clock; Date.now() — лише в composition root" },
  ],
}
