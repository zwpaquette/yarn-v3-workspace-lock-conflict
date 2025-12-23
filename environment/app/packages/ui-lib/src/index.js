import React from 'react'

export function Button ({ children }) {
  return React.createElement('button', {}, children)
}

export function Input ({ value, onChange }) {
  return React.createElement('input', { value, onChange })
}
