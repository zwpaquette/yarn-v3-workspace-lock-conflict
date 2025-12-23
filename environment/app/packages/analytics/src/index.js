import React from 'react'
import { Button } from '@monorepo/ui-lib'

export function Analytics () {
  const [events, setEvents] = React.useState([])

  const trackEvent = () => {
    setEvents([...events, { timestamp: Date.now() }])
  }

  return React.createElement(
    'div',
    {},
    React.createElement('p', {}, `Events: ${events.length}`),
    React.createElement(Button, { onClick: trackEvent }, 'Track Event')
  )
}
