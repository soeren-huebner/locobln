/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 * @flow strict-local
 */
import 'react-native-gesture-handler';
import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import {
  SafeAreaView,
  StyleSheet,
  ScrollView,
  View,
  Text,
  StatusBar,
  Button,
  Dimensions,
} from 'react-native';

import { Overlay } from 'react-native-elements';

import {
  Header,
  LearnMoreLinks,
  Colors,
  DebugInstructions,
  ReloadInstructions,
} from 'react-native/Libraries/NewAppScreen';

import Video from 'react-native-video';

import MapView, { Marker } from 'react-native-maps';

const Stack = createStackNavigator();

const MyStack = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen
          name="Map"
          component={MapScreen}
          options={{ title: 'Map' }}
        />
        <Stack.Screen name="Video" component={VideoScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};


const MapScreen = ({ navigation }) => {
  const exampleMarkers = [
    {
      latitude: 52.43,
      longitude: 13.34,
      title: "EXAMPLE",
      description: "example marker",
      key: '00',
    },
  ];

  const [markers, updateMarkers] = useState(exampleMarkers);

  useEffect(() => {
    fetch('https://locobln.uber.space/markers')
      .then(res => res.json())
      .then(data => { updateMarkers(data.data); });
  }, []);

  return (
    <>
      <StatusBar barStyle="dark-content" />
      <View style={styles.container}>
        <MapView
        style = {styles.mapcontainer}
        initialRegion={{
          latitude: 52.43,
          longitude: 13.34,
          latitudeDelta: 1.0,
          longitudeDelta: 0.5,
        }}>
          
          {markers.map(marker => (
            <Marker
              coordinate={{latitude: marker.latitude, longitude: marker.longitude,}}
              pinColor={marker.color}
              title={marker.title}
              description={marker.description}
              onCalloutPress={() =>
                navigation.navigate('Video', { param: 'jupiters_auroras' })
              }
              key={marker.key}
            />
          ))}

        </MapView>
      </View>
    </>
  );
};

const VideoScreen = ( { route } ) => {
  const { param } = route.params;

  return (
    <Video source={{uri: 'https://locobln.uber.space/video/'+ param +'.mp4' }} style={styles.backgroundVideo} />
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  mapcontainer: {
    flex: 1,
    width: Dimensions.get('window').width,
    height: Dimensions.get('window').height,
  },
  backgroundVideo: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  },
});

export default MyStack;
