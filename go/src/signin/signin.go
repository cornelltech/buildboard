package signin

import (
	"fmt"
	"html/template"
	"io"
	"log"
	"net/http"
	"regexp"
	"strconv"
	"strings"
	"time"

	//	"lcs"

	"appengine"
	"appengine/blobstore"
	"appengine/datastore"
	"appengine/user"

	"github.com/gorilla/mux"
)

const FALL = 0
const SPRING = 1

const STARTUP_STUDIO_URL_ACCESS_KEY = "ccfec1ebbb954e4d6b5fd3aaa682377f524c6ab85efd550af80b0d066b821ac6"

type Period struct {
	Semester int //either SPRING or FALL
	Year     int
}

//a Tile represents a slot for a team on the buildboard
type Tile struct {
	Name       string    //team's company
	Number     int       //identifier for team within company
	Desc       string    //narrative
	Category   string    //company challenge question
	Imgref     string    //company logo
	Members    []string  //who is on this team
	Creator    string    //who made the tile
	CanEdit    []string  //who can edit this tile
	LastUpdate time.Time //last update
	UpdatedBy  string    //who updated it last
	Period     Period    //semester and year
}

//the user's logged in status as a struct wrapper
type Status struct {
	LoggedIn    bool
	CurrentUser *user.User
}

func (s *Status) reset() {
	s.LoggedIn = false
	s.CurrentUser = nil
}

func (s *Status) set(b bool, u *user.User) {
	s.LoggedIn = b
	s.CurrentUser = u
}

func contains(s []string, a string) bool {
	for _, b := range s {
		if strings.EqualFold(strings.TrimSpace(a),strings.TrimSpace(b)) {
			return true
		}
	}
	return false
}

func (p *Period) String() string {
	return fmt.Sprintf("%v_%v", p.Semester, p.Year)
}

func strint(a string, b int) string {
	return a + "_" + strconv.Itoa(b)
}

//google app engine init function
func init() {
	r := mux.NewRouter()
	r.HandleFunc("/", ProjectListHandler)
	r.HandleFunc("/{accessToken}", ProjectListHandler)
	r.HandleFunc("/{year:[0-9]+}/{semester}", ProjectListHandler)
	r.HandleFunc("/{year:[0-9]+}/{semester}/{accessToken}", ProjectListHandler)

	r.HandleFunc("/carousel", carousel)
	r.HandleFunc("/carousel/{accessToken}", carousel)

	r.HandleFunc("/submit", submit)
	r.HandleFunc("/submit/{accessToken}", submit)

	//handler for serving static files (css, html)
	fs := http.FileServer(http.Dir("static"))
	http.Handle("/static/", http.StripPrefix("/static", fs))
	//handle google authentication
	http.HandleFunc("/login", login)
	http.HandleFunc("/logout", logout)
	//handles creation of new tile


	http.HandleFunc("/serve/", serve)

	http.HandleFunc("/delete/", delete)

	http.HandleFunc("/edit", edit)

	http.HandleFunc("/semester", semester)
	http.HandleFunc("/about", about)
	//handles root view
	http.Handle("/", r)
}

func login(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	u := user.Current(c)
	//use GAE's redirect to google login if user is not logged in
	if u == nil {
		url, err := user.LoginURL(c, "/")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Location", url)
		w.WriteHeader(http.StatusFound)
		return
	}
	w.Header().Set("Location", "/")
	w.WriteHeader(http.StatusFound)
	return
}

func logout(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	u := user.Current(c)
	//requires user to be logged in
	if u != nil {
		url, err := user.LogoutURL(c, "/")
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Location", url)
		w.WriteHeader(http.StatusFound)
		return
	} else {
		http.Error(w, "Tried to log out while already logged out", http.StatusInternalServerError)
	}
}

//serves as the ancestor entity for the datastore
//helps with strong consistency for child entities
func tileRootKey(c appengine.Context, semester int, year int) *datastore.Key {
	now_str := fmt.Sprintf("%v_%v", semester, year)
	return datastore.NewKey(c, "Tile", now_str, 0, nil)
}

func CCRoot(c appengine.Context) *datastore.Key {
	return datastore.NewKey(c, "Date", "company_challenges", 0, nil)
}

func SSRoot(c appengine.Context) *datastore.Key {
	return datastore.NewKey(c, "Date", "startup_studio", 0, nil)
}

//keep track of what the current semester is on the server side
func currentSemesterKey(c appengine.Context) *datastore.Key {
	return datastore.NewKey(c, "Date", "current", 0, nil)
}


func ProjectListHandler(w http.ResponseWriter, r *http.Request) {

	urlParams := mux.Vars(r)

	c := appengine.NewContext(r)
	//log.Println(c)
	u := user.Current(c)
	//need to check if user is logged in so that the login/logout button
	//is toggled correctly
	var status *Status = &Status{LoggedIn: false, CurrentUser: nil}
	if u == nil {
		status.reset()
	} else if matched, _ := regexp.MatchString(".*@cornell.edu", u.String()); !matched && !u.Admin {
		status.reset()
		http.Redirect(w, r, "/logout", http.StatusFound)
	} else {
		status.set(true, u)
	}
	var now Period
	e1 := datastore.Get(c, currentSemesterKey(c), &now)
	log.Printf("The value of now is %v", &now)
	if e1 != nil {
		if e1 == datastore.ErrNoSuchEntity {
			now.Semester = 0
			now.Year = 2015
			updateSemesterData(c, &now)
		} else {
			log.Println("DATASTORE PERIOD ERROR")
			http.Error(w, e1.Error(), http.StatusInternalServerError)
		}
	}

	semesterParam, semesterExists := urlParams["semester"]
	yearParam, yearExists := urlParams["year"]

	semesterRequested := now
	if semesterExists && yearExists {
		year, year_parse_err := strconv.Atoi(yearParam)
		isValidSem := strings.EqualFold(semesterParam, "fall") || strings.EqualFold(semesterParam, "spring")
		if (isValidSem && year_parse_err == nil) {
			semesterRequested.Semester = semesterStringToCode(semesterParam)
			semesterRequested.Year = year
		}
	}

	tileKey := tileRootKey(c, semesterRequested.Semester, semesterRequested.Year)

	qs := datastore.NewQuery("Tile").Ancestor(tileKey).Order("-LastUpdate")
	tiles := make([]Tile, 0)
	if _, err := qs.GetAll(c, &tiles); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	ccperiods := make([]Period, 0)
	ssperiods := make([]Period, 0)
	fallqs := datastore.NewQuery("Date").Ancestor(CCRoot(c)).Order("-Semester").Order("-Year")
	springqs := datastore.NewQuery("Date").Ancestor(SSRoot(c)).Order("-Semester").Order("-Year")
	fallqs.GetAll(c, &ccperiods)
	springqs.GetAll(c, &ssperiods)
	log.Println(ccperiods, ssperiods)
	//debug
	//log.Print(tiles)

	urlAccessKey, urlAccessKeyExists := urlParams["accessToken"]
	isCurrentSemesterSpring := now.Semester == SPRING
	isURLForCurrentSemester := semesterRequested == now
	isAccessKeyValid := urlAccessKeyExists && urlAccessKey == STARTUP_STUDIO_URL_ACCESS_KEY
	showStaticTextNoTiles := isURLForCurrentSemester && isCurrentSemesterSpring && !isAccessKeyValid

	semesterURLWithAccessKey := func(year int, semester int) string {
		if urlAccessKeyExists {
			return fmt.Sprintf("/%d/%s/%s", year, semesterCodeToString(semester), urlAccessKey)
		} else {
			return fmt.Sprintf("/%d/%s", year, semesterCodeToString(semester))
		}
	}

	carouselURL := "/carousel"
	if urlAccessKeyExists {
		carouselURL = fmt.Sprintf("/carousel/%s", urlAccessKey)
	}

	submitURL := "/submit"
	if urlAccessKeyExists {
		submitURL = fmt.Sprintf("/submit/%s", urlAccessKey)
	}

	//serve the root template
	funcMap := template.FuncMap{
		"divide":   div,
		"incr":     incr,
		"cong":     congz,
		"ustring":  ustring,
		"contains": contains,
		"isAdmin":  isAdmin,
		"netID":    netID,
		"format":   fmtMembers,
		"semesterURLWithAccessKey": semesterURLWithAccessKey,
	}

	//	fp3 := path.Join("templates", "welcome.html")
	templ := template.Must(template.New("welcome.html").Funcs(funcMap).ParseFiles("templates/welcome.html"))
	//obtain a new uploadURL for team photo, for blobstore
	uploadURL, err := blobstore.UploadURL(c, submitURL, nil)
	if err != nil {
		panic("oh no!")
	}
	w.Header().Set("Content-Type", "text/html")
	templ.Execute(w, map[string]interface{}{
		"Tiles":     tiles,
		"LoggedIn":  status,
		"uploadURL": uploadURL,
		"ccs":       ccperiods,
		"sss":       ssperiods,
		"semesterRequested":       semesterRequested,
		"showStaticTextNoTiles":	showStaticTextNoTiles,
		"carouselURL": carouselURL,
	})
}


func semesterCodeToString(code int) string {
	if(code == SPRING) {
		return "spring"
	} else if(code == FALL){
		return "fall"
	} else {
		panic("Semester code is invalid. Cannot convert to string ")
	}
}

func semesterStringToCode(semesterStr string) int {
	if strings.EqualFold(semesterStr, "spring") {
		return SPRING
	} else if strings.EqualFold(semesterStr, "fall") {
		return FALL
	} else {
		panic("Semester code is invalid. Cannot convert to string ")
	}
}


func div(a int, b int) int {
	return a / b
}

//hardcoded increment modulo 2
func incr(a int) int {
	return (a + 1) % 2
}

//hardcoded test for even-ness
func congz(a int) bool {
	return a%2 == 0
}

//hardcoded tests for new row for the carousel
func congzb(a int) bool {
	return a%12 == 0
}

func congzc(a int) bool {
	return a%12 == 11
}

func ustring(u *user.User) string {
	if u == nil {
		return ""
	} else {
		return u.String()
	}
}

func isAdmin(u *user.User) bool {
	if u == nil {
		return false
	}
	return u.Admin
}

func netID(u string) string {
	return regexp.MustCompile("@").Split(u, 2)[0]
}

func fmtMembers(arr []string) string {
	return strings.Join(arr, ", ")
}

func submit(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	blobs, other, err := blobstore.ParseUpload(r)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		w.Header().Set("Content-type", "text/plain")
		io.WriteString(w, "Internal Server Error")
		c.Errorf("%v", err)
		return
	}
	members := regexp.MustCompile(",").Split(string(other["inputGroup"][0]), -1)
	editors := regexp.MustCompile(",").Split(string(other["inputEditors"][0]), -1)
	var now Period
	datastore.Get(c, currentSemesterKey(c), &now)
	log.Println(now)
	count, cnterr := datastore.NewQuery("Tile").Ancestor(tileRootKey(c, now.Semester, now.Year)).Filter("Name =", string(other["inputName"][0])).Count(c)
	if cnterr != nil {
		log.Println("Something failed with counting for some reason")
	}
	newdata := Tile{
		Name:       string(other["inputName"][0]),
		Number:     count,
		Desc:       string(other["textArea"][0]),
		Category:   string(other["inputCategory"][0]),
		Imgref:     string(blobs["inputFile"][0].BlobKey),
		Members:    members,
		Creator:    user.Current(c).String(),
		CanEdit:    editors,
		LastUpdate: time.Now(),
		UpdatedBy:  string(user.Current(c).String()),
		Period:     now,
	}
	log.Println(newdata)
	key := datastore.NewKey(c, "Tile", strint(newdata.Name, count), 0, tileRootKey(c, now.Semester, now.Year))
	_, keyerr := datastore.Put(c, key, &newdata)
	if keyerr != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	urlParams := mux.Vars(r)

	urlAccessKey, urlAccessKeyExists := urlParams["accessToken"]
	redirectUrl := "/"
	if urlAccessKeyExists {
		redirectUrl = fmt.Sprintf("/%s", urlAccessKey)
	}
	//	log.Println(w.Header)
	http.Redirect(w, r, redirectUrl, http.StatusFound)
}

//for serving images, using the blobkey we stored in the datastore
func serve(w http.ResponseWriter, r *http.Request) {
	blobstore.Send(w, appengine.BlobKey(r.FormValue("blobKey")))
}

func delete(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	var dTile Tile
	//	var now Period
	//	datastore.Get(c, currentSemesterKey(c), &now)
	num, e := strconv.Atoi(r.FormValue("num"))
	sem, e1 := strconv.Atoi(r.FormValue("semester"))
	yr, e2 := strconv.Atoi(r.FormValue("year"))
	if e != nil || e1 != nil || e2 != nil {
		panic("shouldn't happen; semester and year guaranteed to be ints")
	}
	k := datastore.NewKey(c, "Tile", strint(r.FormValue("name"), num), 0, tileRootKey(c, sem, yr))
	datastore.Get(c, k, &dTile)
	if u := user.Current(c); !u.Admin {
		http.Redirect(w, r, "/", http.StatusFound)
		return
	} else {
		log.Println("deleting things now...")
		e1 := blobstore.Delete(c, appengine.BlobKey(dTile.Imgref))
		e2 := datastore.Delete(c, k)
		if e1 != nil {
			log.Println("error with blobstore delete")
		}
		if e2 != nil {
			log.Println("error with datastore delete")
		}
	}
	log.Println("redirecting")
	http.Redirect(w, r, "/", http.StatusFound)
}

func edit(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	var now Period
	datastore.Get(c, currentSemesterKey(c), &now)
	arr := regexp.MustCompile("_").Split(r.FormValue("id"), 4)
	name := arr[0]
	count, cnterr := strconv.Atoi(arr[1])
	if cnterr != nil {
		log.Println("Something failed with counting for some reason")
	}

	sem, e1 := strconv.Atoi(arr[2])
	yr, e2 := strconv.Atoi(arr[3])
	if e1 != nil || e2 != nil {
		panic("neither year nor sem should be non-ints")
	}
	if now.Semester == sem && now.Year == yr {
		value := r.FormValue("value")
		k := datastore.NewKey(c, "Tile", strint(name, count), 0, tileRootKey(c, sem, yr))
		var uTile Tile
		datastore.Get(c, k, &uTile)
		//	log.Println(lcs.Diff(value, uTile.Desc))
		uTile.Desc = value
		uTile.LastUpdate = time.Now()
		datastore.Put(c, k, &uTile)
		w.Write([]byte(uTile.Desc))
	} else {
		w.Write([]byte("Edits discarded: cannot edit entries after the semester has ended"))
	}
}

func semester(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	var now Period
	sem_str := r.FormValue("inputSemester")
	yr_str := r.FormValue("inputYear")
	var sem int
	log.Println(sem_str)
	log.Println(yr_str)
	if sem_str == "Spring" {
		sem = SPRING
	} else if sem_str == "Fall" {
		sem = FALL
	} else {
		log.Println("passed in a semester that isn't spring or fall")
	}
	yr, err := strconv.Atoi(yr_str)
	if err != nil {
		panic("parse error; year passed in is not an int")
	}
	now.Semester = sem
	now.Year = yr
	updateSemesterData(c, &now)
	http.Redirect(w, r, "/", http.StatusFound)
}

func updateSemesterData(c appengine.Context, p *Period) {
	var k *datastore.Key
	if p.Semester == FALL {
		k = datastore.NewKey(c, "Date", p.String(), 0, CCRoot(c))
	} else {
		k = datastore.NewKey(c, "Date", p.String(), 0, SSRoot(c))
	}
	//insert the new semester into the list of all available semesters and replace the current semester
	datastore.Put(c, k, p)
	datastore.Put(c, currentSemesterKey(c), p)
}

func carousel(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	//log.Println(c)
	u := user.Current(c)
	//need to check if user is logged in so that the login/logout button
	//is toggled correctly
	var status *Status = &Status{LoggedIn: false, CurrentUser: nil}
	if u == nil {
		status.reset()
	} else if matched, _ := regexp.MatchString(".*@cornell.edu", u.String()); !matched && !u.Admin{
		status.reset()
		http.Redirect(w, r, "/logout", http.StatusFound)
	} else {
		status.set(true, u)
	}
	var now Period
	datastore.Get(c, currentSemesterKey(c), &now)

	urlParams := mux.Vars(r)
	urlAccessKey, urlAccessKeyExists := urlParams["accessToken"]
	isCurrentSemesterSpring := now.Semester == SPRING
	isAccessKeyValid := urlAccessKeyExists && urlAccessKey == STARTUP_STUDIO_URL_ACCESS_KEY
	showStaticTextNoTiles :=  isCurrentSemesterSpring && !isAccessKeyValid


	qs := datastore.NewQuery("Tile").Ancestor(tileRootKey(c, now.Semester, now.Year))
	tiles := make([]Tile, 0, 10)
	if isAccessKeyValid {
		if _, err := qs.GetAll(c, &tiles); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	}
	ccperiods := make([]Period, 0)
	ssperiods := make([]Period, 0)
	fallqs := datastore.NewQuery("Date").Ancestor(CCRoot(c)).Order("-Semester").Order("-Year")
	springqs := datastore.NewQuery("Date").Ancestor(SSRoot(c)).Order("-Semester").Order("-Year")
	fallqs.GetAll(c, &ccperiods)
	springqs.GetAll(c, &ssperiods)
	//debug
	//log.Print(tiles)



	semesterURLWithAccessKey := func(year int, semester int) string {
		if urlAccessKeyExists {
			return fmt.Sprintf("/%d/%s/%s", year, semesterCodeToString(semester), urlAccessKey)
		} else {
			return fmt.Sprintf("/%d/%s", year, semesterCodeToString(semester))
		}
	}




	carouselURL := "/carousel"
	if urlAccessKeyExists {
		carouselURL = fmt.Sprintf("/carousel/%s", urlAccessKey)
	}

	funcMap := template.FuncMap{
		"divide":   div,
		"incr":     incr,
		"cong":     congz,
		"congb":    congzb,
		"congc":    congzc,
		"ustring":  ustring,
		"contains": contains,
		"isAdmin":  isAdmin,
		"netID":    netID,
		"format":   fmtMembers,
		"semesterURLWithAccessKey": semesterURLWithAccessKey,
	}

	//	fp3 := path.Join("templates", "welcome.html")
	templ := template.Must(template.New("carousel.html").Funcs(funcMap).ParseFiles("templates/carousel.html"))
	//obtain a new uploadURL for team photo, for blobstore
	w.Header().Set("Content-Type", "text/html")
	templ.Execute(w, map[string]interface{}{
		"Tiles":    tiles,
		"LoggedIn": status,
		"ccs":      ccperiods,
		"sss":      ssperiods,
		"semesterRequested":      now,
		"showStaticTextNoTiles":	showStaticTextNoTiles,
		"carouselURL": carouselURL,
	})
}

func about(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	//log.Println(c)
	u := user.Current(c)
	//need to check if user is logged in so that the login/logout button
	//is toggled correctly
	var status *Status = &Status{LoggedIn: false, CurrentUser: nil}
	if u == nil {
		status.reset()
	} else if matched, _ := regexp.MatchString(".*@cornell.edu", u.String()); !matched  && !u.Admin{
		status.reset()
		http.Redirect(w, r, "/logout", http.StatusFound)
	} else {
		status.set(true, u)
	}
	var now Period
	datastore.Get(c, currentSemesterKey(c), &now)

	qs := datastore.NewQuery("Tile").Ancestor(tileRootKey(c, now.Semester, now.Year))
	tiles := make([]Tile, 0, 10)
	if _, err := qs.GetAll(c, &tiles); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	ccperiods := make([]Period, 0)
	ssperiods := make([]Period, 0)
	fallqs := datastore.NewQuery("Date").Ancestor(CCRoot(c)).Order("-Semester").Order("-Year")
	springqs := datastore.NewQuery("Date").Ancestor(SSRoot(c)).Order("-Semester").Order("-Year")
	fallqs.GetAll(c, &ccperiods)
	springqs.GetAll(c, &ssperiods)
	//debug
	//log.Print(tiles)
	funcMap := template.FuncMap{
		"divide":   div,
		"incr":     incr,
		"cong":     congz,
		"ustring":  ustring,
		"contains": contains,
		"isAdmin":  isAdmin,
		"netID":    netID,
		"format":   fmtMembers,
	}

	//	fp3 := path.Join("templates", "welcome.html")
	templ := template.Must(template.New("about.html").Funcs(funcMap).ParseFiles("templates/about.html"))
	//obtain a new uploadURL for team photo, for blobstore
	w.Header().Set("Content-Type", "text/html")
	templ.Execute(w, map[string]interface{}{
		"Tiles":    tiles,
		"LoggedIn": status,
		"ccs":      ccperiods,
		"sss":      ssperiods,
		"now":      now,
	})

}
