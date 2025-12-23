import React from 'react'
import { Button, Input } from '@monorepo/ui-lib'

export function Dashboard () {
  const [value, setValue] = React.useState('')

  return React.createElement(
    'div',
    {},
    React.createElement(Input, {
      value,
      onChange: e => setValue(e.target.value)
    }),
    React.createElement(Button, {}, 'Submit')
  )
}
