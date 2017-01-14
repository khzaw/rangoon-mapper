import types  from '../constants/ActionTypes';

const initialState = {
    center: {lat: 16.7943528, lng: 96.1518985},
    zoom: 14
}

const map = (state = initialState, action) => {
  switch (action.type) {
    case types.PLACES_CHANGED:
      const location = action.places[0].geometry.location;
      const center = { lat: location.lat(), lng: location.lng() }
      return Object.assign({}, state, {
          center: center,
      })
    default:
      return state
  }
}

export default map
